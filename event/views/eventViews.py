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
                    return self.publish_to_all_group(event)
                elif target_audience == 'm':
                    return self.publish_to_males_group(event)
                elif target_audience == 'f':
                    return self.publish_to_females_group(event)
                return render(self.request, 'eventTemplates/publishEvent/publishToAll.html', {'event': published_event})
        except:
            messages.error(self.request,'Somthing went wrong during publishing the event')
            return super().form_invalid(form)
        
    def publish_to_all_group(self, event):
            group = Group.objects.get(name='ALL')
            PublishedEvent.objects.create(event=event, target_audience=group)
            event.is_published = True
            event.save()
            messages.success(self.request, 'Event has been published successfully!')
            return redirect(reverse('event:event-detail', kwargs={'pk': event.pk}))
    
    def test_func(self):
        return self.request.user.is_superuser
    




