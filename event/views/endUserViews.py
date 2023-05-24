from django.views.generic import ListView,View
from ..models import PublishedEvent,RegisteredEvent,Attendees,HeldEvent
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import get_template
import pdfkit
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from authentication.utilities import get_MSAL_user

ms_identity_web = settings.MS_IDENTITY_WEB


@method_decorator(ms_identity_web.login_required,name="dispatch")
class EndUserPublishedEventListView(UserPassesTestMixin,ListView):
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
        user = get_MSAL_user(self.request, ms_identity_web)
        group_ids=user.groups.values_list('id',flat=True)
        registered_event_ids = RegisteredEvent.objects.filter(user=user).values_list('published_event__event_id', flat=True)
        attended_event_ids=Attendees.objects.filter(user=user).values_list('held_event__published_event__event_id',flat=True)
        return PublishedEvent.objects.filter(
            Q(target_audience__id__in=group_ids) &
            Q(event__date__gte=today) & 
            ~Q(event_id__in=registered_event_ids)&
            ~Q(event_id__in=attended_event_ids))
    
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return not user.is_superuser
    
    def handle_no_permission(self):
        return redirect('event:admin-dash')


@method_decorator(ms_identity_web.login_required,name="dispatch")
class RegisteredEventsListView(UserPassesTestMixin,ListView):
    model=RegisteredEvent
    template_name='endUserTemplates/registered_events.html'
    # context_object_name='registered_events'
    paginate_by=5

    def get_queryset(self):
        user = get_MSAL_user(self.request, ms_identity_web)
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

    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return not user.is_superuser
    
    

@method_decorator(ms_identity_web.login_required,name="dispatch")
class EventsHistoryView(UserPassesTestMixin,ListView):
    model=Attendees
    template_name='endUserTemplates/user_history.html'
    paginate_by=5

    def get_queryset(self):
        user=get_MSAL_user(self.request, ms_identity_web)
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
    
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return not user.is_superuser   
    
    
@method_decorator(ms_identity_web.login_required,name="dispatch")
class GenerateCertificateView(UserPassesTestMixin,View):
    def post(self,request,pk):
        if self.request.method=='POST':
            user=get_MSAL_user(self.request, ms_identity_web)
            event=HeldEvent.objects.get(id=pk)
            attendee=Attendees.objects.filter(user=user,held_event=event)
            if attendee:
                context = {
                    'user': user,
                    'event': event,
                    'date': event.published_event.event.date,
                }
                template = get_template('endUserTemplates/certificate.html')
                html = template.render(context)
                pdf = pdfkit.from_string(html, False)

                # Create a new HTTP response with the PDF document
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="certificate.pdf"'
                return response
            else:
                return HttpResponseBadRequest("Can't generate the certificate at the moment")
            
        else: 
            return HttpResponseBadRequest("Invalid request method")
        
    def test_func(self):
        user = get_MSAL_user(self.request, ms_identity_web)
        return not user.is_superuser
