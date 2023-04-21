from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,View
from ..models import PublishedEvent,RegisteredEvent,Attendees,HeldEvent
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from reportlab.pdfgen import canvas
from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import get_template
import pdfkit


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
    
    
@method_decorator(login_required(login_url='authentication:login'),name="dispatch") 
class GenerateCertificateView(View):
    def post(self,request,pk):
        if self.request.method=='POST':
            # user=self.request.user
            # print(user)
            # event=HeldEvent.objects.get(id=pk)
            # print(event)
            # #check attendee
            # attendee=Attendees.objects.filter(user=user,held_event=event)
            # print(attendee)
            # if attendee:
            #         email=user.email
            #         #first_name=user.first_name
            #         #last_name=user.last_name
            #         date=event.published_event.event.date

            #         # Create a new PDF document
            #         response = HttpResponse(content_type='application/pdf')
            #         response['Content-Disposition'] = 'inline; filename="certificate.pdf"'
            #         p = canvas.Canvas(response)

            #         # Add the certificate content
            #         p.drawString(100, 750, "Certificate of Attendance")
            #         p.drawString(100, 700, f"This certificate is presented to {user.email} in recognition of their attendance at {event.published_event.event.name} held on {event.published_event.event.date}. This serves as a testament to their commitment to learning and personal development. We congratulate {user.email} on their achievement and wish them continued success in their endeavors. ")
            #         # p.drawString(100, 700, f"Name: {name}")
            #         # p.drawString(100, 650, f"Email: {email}")
            #         # p.drawString(100, 600, f"Event: {event_name}")
            #         # p.drawString(100, 550, f"Date Attended: {date_attended}")
            #         # p.drawString(100, 600, f"Date: {date}")

            #         # Close the PDF document
            #         p.showPage()
            #         p.save()
            #         return response

            user=self.request.user
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

    
            