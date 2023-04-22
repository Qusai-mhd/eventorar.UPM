from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from ..models import HeldEvent,Attendees,PublishedEvent,RegisteredEvent
from django.db.models import Count,Q
import pdfkit
from django.template.loader import render_to_string
from datetime import datetime
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

class GenerateReportView(UserPassesTestMixin,TemplateView):
    template_name='reportTemplates/select_report_type.html'

    def test_func(self):
        return self.request.user.is_superuser


class GenerateSemesterBasedReportView(UserPassesTestMixin,View):
    PAGE_SIZE = 'Letter'
    PAGE_MARGIN = {
        'top': '0.5in',
        'right': '0.5in',
        'bottom': '0.5in',
        'left': '0.5in',
    }
    STYLES = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            text-align: left;
            padding: 8px;
        }

        th {
            background-color: #ddd;
        }
    </style>
    """

    def get(self,request):
        if self.request.method=='GET':
            semesters=HeldEvent.objects.values_list('published_event__event__semester',flat=True).distinct()
            return render (self.request,'reportTemplates/select_semester.html',{"semesters":semesters})

    def post(self,request):
        if self.request.method=='POST':
            semester=self.request.POST.get('option',None)
            events=HeldEvent.objects.filter(published_event__event__semester=semester)\
            .annotate(num_males=Count('attendees__user',filter=Q(attendees__user__gender='M')),\
                      num_females=Count('attendees__user',filter=Q(attendees__user__gender='F')))

            total_attendees = sum(event.number_of_attendees for event in events)
            total_males = sum(event.num_males for event in events)
            total_females = sum(event.num_females for event in events)

            user=self.request.user
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            context = {
                'semester': semester,
                'events': events,
                'total_attendees': total_attendees,
                'total_males': total_males,
                'total_females': total_females,
                'user':user,
                'time':time,
            }
            html = render_to_string('reportTemplates/semester_based_report.html', context)

            options = {
                'page-size': self.PAGE_SIZE,
                'margin-top': self.PAGE_MARGIN['top'],
                'margin-right': self.PAGE_MARGIN['right'],
                'margin-bottom': self.PAGE_MARGIN['bottom'],
                'margin-left': self.PAGE_MARGIN['left'],
            }
            pdf = pdfkit.from_string(self.STYLES + html, False, options=options)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="SemesterReport-{semester}.pdf"'
            return response

    def test_func(self):
        return self.request.user.is_superuser
        

class GenerateOrganizerBasedReportView(UserPassesTestMixin,View):
    PAGE_SIZE = 'Letter'
    PAGE_MARGIN = {
        'top': '0.5in',
        'right': '0.5in',
        'bottom': '0.5in',
        'left': '0.5in',
    }
    STYLES = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            text-align: left;
            padding: 8px;
        }

        th {
            background-color: #ddd;
        }
    </style>
    """

    
    def get(self,request):
        if self.request.method=='GET':
            organizers=HeldEvent.objects.values_list('published_event__event__organizer',flat=True).distinct()
            return render (self.request,'reportTemplates/select_organizer.html',{"organizers":organizers})
        
    def post(self,request):
        if self.request.method=='POST':
            organizer=self.request.POST.get('option',None)
            events=HeldEvent.objects.filter(published_event__event__organizer=organizer)\
            .annotate(num_males=Count('attendees__user',filter=Q(attendees__user__gender='M')),\
                      num_females=Count('attendees__user',filter=Q(attendees__user__gender='F')))
            
            total_attendees = sum(event.number_of_attendees for event in events)
            total_males = sum(event.num_males for event in events)
            total_females = sum(event.num_females for event in events)

            user=self.request.user
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            context = {
                'organizer': organizer,
                'events': events,
                'total_attendees': total_attendees,
                'total_males': total_males,
                'total_females': total_females,
                'user':user,
                'time':time,
            }
            html = render_to_string('reportTemplates/organizer_based_report.html', context)

            options = {
                'page-size': self.PAGE_SIZE,
                'margin-top': self.PAGE_MARGIN['top'],
                'margin-right': self.PAGE_MARGIN['right'],
                'margin-bottom': self.PAGE_MARGIN['bottom'],
                'margin-left': self.PAGE_MARGIN['left'],
            }
            pdf = pdfkit.from_string(self.STYLES + html, False, options=options)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="OrganizerReport-{organizer}.pdf"'
            return response

    def test_func(self):
        return self.request.user.is_superuser
    

@method_decorator(require_POST, name='dispatch')
class GenerateEventBasedReport(UserPassesTestMixin,View):
    PAGE_SIZE = 'Letter'
    PAGE_MARGIN = {
        'top': '0.5in',
        'right': '0.5in',
        'bottom': '0.5in',
        'left': '0.5in',
    }
    STYLES = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            text-align: left;
            padding: 8px;
        }

        th {
            background-color: #ddd;
        }
    </style>
    """
    
    def post(self,request,pk):
        event=HeldEvent.objects.filter(id=pk)\
        .annotate(num_males=Count('attendees__user',filter=Q(attendees__user__gender='M')),\
                    num_females=Count('attendees__user',filter=Q(attendees__user__gender='F')))\
                    .select_related('published_event__event')\
                    .first()
        
        user=self.request.user
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        context = {
        'event': event,
        'user':user,
        'time':time
        }
        html = render_to_string('reportTemplates/event_based_report.html', context)

        options = {
            'page-size': self.PAGE_SIZE,
            'margin-top': self.PAGE_MARGIN['top'],
            'margin-right': self.PAGE_MARGIN['right'],
            'margin-bottom': self.PAGE_MARGIN['bottom'],
            'margin-left': self.PAGE_MARGIN['left'],
        }
        pdf = pdfkit.from_string(self.STYLES + html, False, options=options)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="EventReport-{event.published_event.event.name}.pdf"'
        return response  

    def test_func(self):
        return self.request.user.is_superuser
    

@method_decorator(require_POST, name='dispatch')
class AttendeesListView(UserPassesTestMixin,View):
    PAGE_SIZE = 'Letter'
    PAGE_MARGIN = {
        'top': '0.5in',
        'right': '0.5in',
        'bottom': '0.5in',
        'left': '0.5in',
    }
    STYLES = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            text-align: left;
            padding: 8px;
        }

        th {
            background-color: #ddd;
        }
    </style>
    """
    
    def post(self,request,pk):
        event=HeldEvent.objects.get(id=pk)
        attendees=Attendees.objects.filter(held_event=event)
        num_attendees=attendees.count()
        
        context = {
        'event':event,
        'attendees': attendees,
        'attendees_num':num_attendees,
        }
        html = render_to_string('reportTemplates/event_attendees_list.html', context)

        options = {
            'page-size': self.PAGE_SIZE,
            'margin-top': self.PAGE_MARGIN['top'],
            'margin-right': self.PAGE_MARGIN['right'],
            'margin-bottom': self.PAGE_MARGIN['bottom'],
            'margin-left': self.PAGE_MARGIN['left'],
        }
        pdf = pdfkit.from_string(self.STYLES + html, False, options=options)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="AttendeesList-{event.published_event.event.name}.pdf"'
        return response

    def test_func(self):
        return self.request.user.is_superuser
    
    
@method_decorator(require_POST, name='dispatch')
class RegistrantsListView(UserPassesTestMixin,View):
    PAGE_SIZE = 'Letter'
    PAGE_MARGIN = {
        'top': '0.5in',
        'right': '0.5in',
        'bottom': '0.5in',
        'left': '0.5in',
    }
    STYLES = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            text-align: left;
            padding: 8px;
        }

        th {
            background-color: #ddd;
        }
    </style>
    """
    
    def post(self,request,pk):
        event=PublishedEvent.objects.get(id=pk)
        registrants=RegisteredEvent.objects.filter(published_event=event)
        num_registrants=registrants.count()
        
        context = {
        'event':event,
        'registrants': registrants,
        'registrants_num':num_registrants,
        }
        html = render_to_string('reportTemplates/event_registerants_list.html', context)

        options = {
            'page-size': self.PAGE_SIZE,
            'margin-top': self.PAGE_MARGIN['top'],
            'margin-right': self.PAGE_MARGIN['right'],
            'margin-bottom': self.PAGE_MARGIN['bottom'],
            'margin-left': self.PAGE_MARGIN['left'],
        }
        pdf = pdfkit.from_string(self.STYLES + html, False, options=options)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="RegistrantList-{event.event.name}.pdf"'
        return response

    def test_func(self):
        return self.request.user.is_superuser
