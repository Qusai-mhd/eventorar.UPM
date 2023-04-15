from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView,CreateView,DetailView,DeleteView,UpdateView,FormView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..models import Event,PublishedEvent,Group
from ..forms import PublishEventForm

class EventListView(UserPassesTestMixin,ListView):
    model=Event
    template_name='adminTemplates/admin_dashboard.html'
    queryset=Event.objects.filter()
    context_object_name='events'
    # paginate_by=5
    # def get_context_data(self, **kwargs):
    #     context = super(EventListView, self).get_context_data(**kwargs)
    #     events = self.get_queryset()
    #     page = self.request.GET.get('page')
    #     paginator = Paginator(events, self.paginate_by)
    #     try:
    #         events = paginator.page(page)
    #     except PageNotAnInteger:
    #         events = paginator.page(1)
    #     except EmptyPage:
    #         events = paginator.page(paginator.num_pages)
    #     context['events'] = events
    #     return context
    
    def test_func(self):
        return self.request.user.is_superuser
    
class EventCreateView(UserPassesTestMixin,CreateView):
    model=Event
    template_name='eventTemplates/crud/createEvent.html'
    fields='name','organizer','date','time','location','description'
    
    def get_success_url(self):
        return reverse_lazy('event:event-detail',kwargs={'pk':self.object.id})
    
    def test_func(self):
        return self.request.user.is_superuser
    

@method_decorator(login_required, name='dispatch')
class EventDetailView(DetailView):
    model=Event
    template_name='eventTemplates/crud/detail.html'
    context_object_name='event'


class EventUpdateView(UserPassesTestMixin,UpdateView):
    model=Event
    template_name='eventTemplates/crud/update.html'
    queryset=Event.objects.filter()
    context_object_name='event'
    fields='name','organizer','date','time','location','description'
    
    def get_success_url(self):
        return reverse_lazy('event:event-detail',kwargs={'pk': self.object.id})
    
    def test_func(self):
        return self.request.user.is_superuser


class EventDeleteView(UserPassesTestMixin,DeleteView):
    model=Event
    template_name='eventTemplates/crud/delete.html'
    queryset=Event.objects.filter(is_published=False)
    context_object_name='event'
    success_url=reverse_lazy('event:created-events-list')

    def test_func(self):
        return self.request.user.is_superuser


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
    
    def form_valid(self, form):
        target_audience = form.cleaned_data['Target_audience']
        event = self.get_event()
        try:
            with transaction.atomic():
                if target_audience == 'all':
                    return self.publish(event,"All")
                elif target_audience == 'm':
                    return self.publish(event,"Male")
                elif target_audience == 'f':
                    return self.publish(event,"Female")
                return render(self.request, 'eventTemplates/publishEvent/publishToAll.html', {'event': published_event})
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
        return self.request.user.is_superuser
    

class UnpublishEventList(UserPassesTestMixin,ListView):
    model=PublishedEvent
    
    def get_event(self):
        return get_object_or_404(PublishedEvent, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['published_event'] = self.get_event()
        return context
    def get_queryset(self):
        return super().get_queryset()

    def test_func(self):
        return self.request.user.is_superuser