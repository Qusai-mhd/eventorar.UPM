from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse,HttpResponseRedirect
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView,CreateView,DetailView,DeleteView,UpdateView,FormView,View
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..models import Event,PublishedEvent,Group,HeldEvent,RegisteredEvent
from ..forms import PublishEventForm,UnpublishEventForm
from .qrCodeViews import generate_qr_code
from event.tasks import send_qr_code

from django.conf import settings
from authentication.utilities import get_MSAL_user

ms_identity_web = settings.MS_IDENTITY_WEB


@method_decorator(ms_identity_web.login_required, name='dispatch')
class EventListView(UserPassesTestMixin,ListView):
    model=Event
    template_name='adminTemplates/admin_dashboard.html'
    queryset=Event.objects.filter()
    context_object_name='events'
    paginate_by=5
    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        events = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(events, self.paginate_by)
        try:
                events = paginator.page(page)
        except PageNotAnInteger:
                events = paginator.page(1)
        except EmptyPage:
                events = paginator.page(paginator.num_pages)
                context['events'] = events
        return context
    
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser


@method_decorator(ms_identity_web.login_required, name='dispatch')
class EventCreateView(UserPassesTestMixin,CreateView):
    model=Event
    template_name='eventTemplates/crud/createEvent.html'
    fields='name','organizer','date','time','location','description'
    
    
    def get_success_url(self):
        return reverse_lazy('event:event-detail',kwargs={'pk':self.object.id})
    
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser
    

@method_decorator(ms_identity_web.login_required, name='dispatch')
class EventDetailView(UserPassesTestMixin,DetailView):
    model=Event
    template_name='eventTemplates/crud/detail.html'
    context_object_name='event'

    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser


@method_decorator(ms_identity_web.login_required, name='dispatch')
class UserEventDetailView(UserPassesTestMixin,DetailView):
    model=Event
    template_name='endUserTemplates/event_detail.html'
    context_object_name='event'

    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return not user.is_superuser


@method_decorator(ms_identity_web.login_required, name='dispatch')
class EventUpdateView(UserPassesTestMixin,UpdateView):
    model=Event
    template_name='eventTemplates/crud/update.html'
    queryset=Event.objects.filter()
    context_object_name='event'
    fields='name','organizer','date','time','location','description'
    
    def get_success_url(self):
        return reverse_lazy('event:event-detail',kwargs={'pk': self.object.id})
    
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser


@method_decorator(ms_identity_web.login_required, name='dispatch')
class EventDeleteView(UserPassesTestMixin,DeleteView):
    model=Event
    template_name='eventTemplates/crud/delete.html'
    queryset=Event.objects.filter(is_published=False)
    context_object_name='event'
    success_url=reverse_lazy('event:admin-dash')

    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser


@method_decorator(ms_identity_web.login_required, name='dispatch')
class PublishEventView(UserPassesTestMixin,FormView):
    template_name='eventTemplates/publishEvent/publish_event.html'
    form_class=PublishEventForm
    success_url = reverse_lazy('event:event-list')

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_event()
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_event()
        return kwargs
    
    def form_valid(self, form):
        target_audience = form.cleaned_data['Target_audience']
        event = self.get_event()
        try:
            with transaction.atomic(): 
                if target_audience == 'all':
                    return self.publish(event,"All Colleges")
                elif target_audience == 'cs':
                    return self.publish(event,"College Of Computer and Cyber Sciences")
                elif target_audience == 'eng':
                    return self.publish(event,"College Of Engineering")
                elif target_audience == 'bu':
                    return self.publish(event,'College Of Business Administration')
                elif target_audience == 'prep':
                    return self.publish(event,'Prep Year')
                return render(self.request, 'eventTemplates/publishEvent/publishToAll.html')
        except:
            messages.error(self.request,'Somthing went wrong during publishing the event')
            return super().form_invalid(form)
        
    def publish(self, event,t_audience):
            group = Group.objects.get(name=t_audience)
            PublishedEvent.objects.create(event=event, target_audience=group)
            event.is_published = True
            event.save()
            messages.success(self.request, 'Event has been published successfully!')
            return redirect(reverse('event:event-detail', kwargs={'pk': event.id}))
    
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser


@method_decorator(ms_identity_web.login_required, name='dispatch')
class UnPublishEventView(UserPassesTestMixin,FormView):
    model=PublishedEvent
    template_name='eventTemplates/publishEvent/unpublish_event.html'
    success_url=reverse_lazy('event:published_event')
    form_class=UnpublishEventForm               

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['p_event'] = get_object_or_404(PublishedEvent, pk=self.kwargs['pk'])
        return kwargs
   
    def form_valid(self, form):
        event = form.published_event.event
        event.is_published = False
        event.save()
        RegisteredEvent.objects.filter(published_event=form.published_event).delete()
        #Invalidate the related QR codes
        form.published_event.delete()
        messages.success(self.request, 'Event has been unpublished successfully!')
        return super().form_valid(form)

    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return user.is_superuser


@method_decorator(ms_identity_web.login_required,name="dispatch")
class EventRegistrationView(UserPassesTestMixin,View):
    def post(self,request, pk):
        user=get_MSAL_user(self.request, ms_identity_web)
        published_event=PublishedEvent.objects.get(id=pk)
        user_id=user.id
        published_event_id=published_event.id
        try: 
            with transaction.atomic():
                qr_code_buffer=generate_qr_code(request,event_id=published_event_id,user_id=user_id)
                send_qr_code(user_id,published_event_id,qr_code_buffer)
                RegisteredEvent.objects.create(user=user,published_event=published_event)
                published_event.count+=1
                published_event.save()
                messages.success(self.request, "Registered Successfully. A QR code has been sent to your email.")
                return render(self.request,'eventTemplates/registerEvent/success-message.html', {"messages": messages.get_messages(request)})
            
                # if email:
                # else:
                #     messages.error(request, "Can't register for this event at the moment. Try again later or contact the registrar")       
                #     return render(request,'eventTemplates/registerEvent/failure_message.html', {"messages": messages.get_messages(request)})
                # messages.success(self.request,"Registered Successfully. A QR code has been sent to your email.")
                # return render(request,'eventTemplates/registerEvent/success-message.html', {"messages": messages.get_messages(request)})
        except:
            messages.error(self.request,"Can't register for this event! Try again or contact the registrar")
            return render(self.request,'eventTemplates/registerEvent/failure_message.html', {"messages": messages.get_messages(request)})
        
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return not user.is_superuser
