from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from ..models import PublishedEvent,RegisteredEvent,Attendees
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.mail import send_mail

@method_decorator(login_required(login_url='authentication:login'),name="dispatch")
class EndUserPublishedEventListView(ListView):
    model=PublishedEvent
    template_name='endUserTemplates/enduserdash.html'
    context_object_name='events'
    paginate_by=5

    def get_context_data(self, **kwargs):
        context = super(EndUserPublishedEventListView, self).get_context_data(**kwargs)
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
    
    def get_queryset(self):
        today=timezone.now().date()
        user=self.request.user
        group_ids=user.groups.values_list('id',flat=True)
        registered_event_ids = RegisteredEvent.objects.filter(user=user).values_list('published_event__event_id', flat=True)
        return PublishedEvent.objects.filter(
            Q(target_audience__id__in=group_ids) &
            Q(event__date__gte=today) & 
            ~Q(event_id__in=registered_event_ids))
    
@method_decorator(login_required(login_url='authentication:login'),name="dispatch")
class RegisteredEventsListView(ListView):
    model=RegisteredEvent
    template_name='endUserTemplates/registered_events.html'
    # context_object_name='registered_events'
    paginate_by=5

    def get_queryset(self):
        user=self.request.user
        return RegisteredEvent.objects.filter(user=user).order_by('date_of_registration')
    
    def get_context_data(self, **kwargs):
        context = super(RegisteredEventsListView, self).get_context_data(**kwargs)
        events = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(events, self.paginate_by)
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        context['registered_events'] = events
        return context
    

@method_decorator(login_required(login_url='authentication:login'),name="dispatch") 
class EventsHistoryView(ListView):
    model=Attendees
    template_name='endUserTemplates/user_history.html'
    paginate_by=5

    def get_queryset(self):
        user=self.request.user
        return Attendees.objects.filter(user=user).order_by('held_event__published_event__event__date')
    
    def get_context_data(self, **kwargs):
        context = super(EventsHistoryView, self).get_context_data(**kwargs)
        events = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(events, self.paginate_by)
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        context['attended_events'] = events
        return context


    
            