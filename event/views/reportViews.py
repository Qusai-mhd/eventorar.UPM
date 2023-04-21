from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from django.views.generic import View,TemplateView
from ..models import HeldEvent
from django.db.models import Count,Q
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4,landscape


class GenerateReportView(UserPassesTestMixin,TemplateView):
    template_name='reportTemplates/select_report_type.html'

    def test_func(self):
        return self.request.user.is_superuser


class GenerateSemesterBasedReportView(UserPassesTestMixin,View):
    PAGE_HEIGHT = letter[1]
    PAGE_WIDTH = letter[0]
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = styles['Heading4']
    table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black),
                   ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                   ('FONTSIZE', (0, 0), (-1, 0), 14),
                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]

    def get(self,request):
        if self.request.method=='GET':
            semesters=HeldEvent.objects.values_list('published_event__event__semester',flat=True).distinct()
            return render (self.request,'reportTemplates/select_semester.html',{"semesters":semesters})

    def post(self,request):
        if self.request.method=='POST':
            semester=self.request.POST.get('option',None)
            # events=HeldEvent.objects.filter(published_event__event__semester=semester).annotate(num_attendees=Count('attendees'))
            events=HeldEvent.objects.filter(published_event__event__semester=semester)\
            .annotate(num_males=Count('attendees__user',filter=Q(attendees__user__gender='M')),\
                      num_females=Count('attendees__user',filter=Q(attendees__user__gender='F')))


            data = [['Event Name', 'Date', 'Organizer', 'Audience', 'Attendees','Males','Females']]
            # Create a file-like buffer to receive PDF data.
            buffer = BytesIO()

            # Create the PDF object, using the BytesIO object as its "file."
            p = canvas.Canvas(buffer, pagesize=A4)

            # Write the title of the report.
            p.setFont(self.title_style.fontName, self.title_style.fontSize)
            p.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 50, "Semester Report")
            p.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 75, f'{semester}')

            # Write the headers of the table.
            y = self.PAGE_HEIGHT - 150
            y -= self.header_style.leading

            # Write the data rows of the table.
            for event in events:
                row_data = [event.published_event.event.name,
                            str(event.published_event.event.date),
                            event.published_event.event.organizer,
                            str(event.published_event.target_audience),
                            str(event.number_of_attendees),
                            str(event.num_males),
                            str(event.num_females)]
                data.append(row_data)
                
            total_attendees = sum(event.number_of_attendees for event in events)
            p.setFont("Helvetica", 10)
            p.drawString(100, y-40, f"Total number of attendees: {total_attendees}")

            total_males = sum(event.num_males for event in events)
            p.setFont("Helvetica", 10)
            p.drawString(100, y-60, f"Total Males: {total_males}")

            total_females = sum(event.num_females for event in events)
            p.setFont("Helvetica", 10)
            p.drawString(100, y-80, f"Total Females: {total_females}")

            table = Table(data, style=self.table_style)
            table.wrapOn(p, self.PAGE_WIDTH, self.PAGE_HEIGHT)
            table.drawOn(p, 50, y)

            # Close the PDF object cleanly, and we're done.
            p.showPage()
            p.save()

            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename=EventReport.pdf'
            return response

    def test_func(self):
        return self.request.user.is_superuser
        

class GenerateOrganizerBasedReportView(UserPassesTestMixin,View):

    PAGE_HEIGHT = letter[1]
    PAGE_WIDTH = letter[0]
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = styles['Heading4']
    table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black),
                   ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                   ('FONTSIZE', (0, 0), (-1, 0), 8),
                   ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                   ('LEFTPADDING', (0, 0), (-1, -1), 2),
                   ]
    
    def get(self,request):
        if self.request.method=='GET':
            organizers=HeldEvent.objects.values_list('published_event__event__organizer',flat=True).distinct()
            return render (self.request,'reportTemplates/select_organizer.html',{"organizers":organizers})
        
    def post(self,request):
        if self.request.method=='POST':
            organizer=self.request.POST.get('option',None)
            # events=HeldEvent.objects.filter(published_event__event__semester=semester).annotate(num_attendees=Count('attendees'))
            events=HeldEvent.objects.filter(published_event__event__organizer=organizer)\
            .annotate(num_males=Count('attendees__user',filter=Q(attendees__user__gender='M')),\
                      num_females=Count('attendees__user',filter=Q(attendees__user__gender='F')))

            data = [['Event Title', 'Date','Time','Audience','Attendees','Maless','Females','Semester']]
            # Create a file-like buffer to receive PDF data.
            buffer = BytesIO()

            # Create the PDF object, using the BytesIO object as its "file."
            p = canvas.Canvas(buffer, pagesize=A4)

            # Write the title of the report.
            p.setFont(self.title_style.fontName, self.title_style.fontSize)
            p.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 50, "Organizer Report")
            p.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 75, f'{organizer}')

            # Write the headers of the table.
            y = self.PAGE_HEIGHT - 150
            y -= self.header_style.leading

            # Write the data rows of the table.
            for event in events:
                row_data = [event.published_event.event.name,
                            str(event.published_event.event.date),
                            str(event.published_event.event.time),
                            str(event.published_event.target_audience),
                            str(event.number_of_attendees),
                            str(event.num_males),
                            str(event.num_females),
                            event.published_event.event.semester]
                data.append(row_data)
                
            total_attendees = sum(event.number_of_attendees for event in events)
            p.setFont("Helvetica", 10)
            p.drawString(100, y-40, f"Total number of attendees: {total_attendees}")

            total_males = sum(event.num_males for event in events)
            p.setFont("Helvetica", 10)
            p.drawString(100, y-60, f"Total Males: {total_males}")

            total_females = sum(event.num_females for event in events)
            p.setFont("Helvetica", 10)
            p.drawString(100, y-80, f"Total Females: {total_females}")

            table = Table(data, style=self.table_style)
            table.wrapOn(p, self.PAGE_HEIGHT, self.PAGE_WIDTH)
            table.drawOn(p, 50, y)

            # Close the PDF object cleanly, and we're done.
            p.showPage()
            p.save()

            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename=EventReport.pdf'
            return response
        

    def test_func(self):
        return self.request.user.is_superuser
    

class GenerateEventBasedReport(UserPassesTestMixin,View):
    PAGE_HEIGHT = letter[1]
    PAGE_WIDTH = letter[0]
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = styles['Heading4']
    table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black),
                   ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                   ('FONTSIZE', (0, 0), (-1, 0), 8),
                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]
    
    def post(self,request,pk):
        if self.request.method=='POST':
            event=HeldEvent.objects.filter(id=pk)\
            .annotate(num_males=Count('attendees__user',filter=Q(attendees__user__gender='M')),\
                      num_females=Count('attendees__user',filter=Q(attendees__user__gender='F')))\
                      .select_related('published_event__event')\
                      .first()
            print(event)
            
            data = [['Date','Time','Location','Audience', 'Registered','Attendees','Maless','Females','Semester']]
            # Create a file-like buffer to receive PDF data.
            buffer = BytesIO()

            # Create the PDF object, using the BytesIO object as its "file."
            p = canvas.Canvas(buffer, pagesize=A4)

            # Write the title of the report.
            p.setFont(self.title_style.fontName, self.title_style.fontSize)
            p.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 50, "Event Report")
            p.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 75, f'{event.published_event.event.name}')

            # Write the headers of the table.
            y = self.PAGE_HEIGHT - 150
            y -= self.header_style.leading

            # Write the data rows of the table.
            row_data = [str(event.published_event.event.date),
                        str(event.published_event.event.time),
                        str(event.published_event.event.location),
                        str(event.published_event.target_audience),
                        str(event.published_event.count),
                        str(event.number_of_attendees),
                        str(event.num_males),
                        str(event.num_females),
                        event.published_event.event.semester]
            
            data.append(row_data)
            table = Table(data, style=self.table_style)

            table.wrapOn(p, self.PAGE_HEIGHT, self.PAGE_WIDTH)
            table.drawOn(p, 50, y)

            # Close the PDF object cleanly, and we're done.
            p.showPage()
            p.save()

            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename=EventReport.pdf'
            return response
        

    def test_func(self):
        return self.request.user.is_superuser

