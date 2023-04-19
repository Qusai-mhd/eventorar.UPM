from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings


# Create your models here.
class EndUser(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    email=models.EmailField(unique=True)
    gender=models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        permissions=(
            ("can_register_in_all_published_events","To register in all events"),
            ("can_register_in_male_published_events","To register in male events"),
            ("can_register_in_female_published_events","To register in female events"),
        )

class Event(models.Model):
    SE_CLUB='SE'
    FC_CLUB='FC'
    CARCH_CLUB='CARCH'
    CE_CLUB='CE'
    MEDIA_CLUB='MEDIA'
    AI_CLUB='AI'
    OTHERS='OTHERS'
    ORGANIZER_CHOICES=[
        (SE_CLUB,'SE CLUB'),
        (FC_CLUB,'FC CLUB'),
        (CARCH_CLUB,'C ARCH CLUB'),
        (CE_CLUB,'CIVIL ENGINEERING CLUB'),
        (MEDIA_CLUB,'MEDIA CLUB'),
        (AI_CLUB,'AI CLUB'),
        (OTHERS,'OTHERS'),
    ]

    name=models.CharField(max_length=255)
    organizer=models.CharField(max_length=50,choices=ORGANIZER_CHOICES,default=OTHERS)
    date=models.DateField()
    time=models.TimeField()
    location=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    semester=models.CharField(max_length=255)
    is_published=models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.date.month in [8,9,10,11,12]:
            self.semester=f'Acad Year {self.date.year} - {self.date.year+1} Fall'
        elif self.date.month in [1,2,3,4,5,6]:
            self.semester=f'Acad Year {self.date.year-1} - {self.date.year} Spring'
        super(Event,self).save(*args,**kwargs)

    def __str__(self) -> str:
        return self.name
    class Meta:
        ordering=['name']
        

class PublishedEvent(models.Model):
    event=models.OneToOneField(Event,on_delete=models.CASCADE)
    target_audience=models.ForeignKey(Group, on_delete=models.CASCADE)
    date_of_publication=models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.event.name
    class Meta:
        ordering=['date_of_publication']
    
class RegisteredEvent(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    published_event=models.ForeignKey(PublishedEvent,on_delete=models.CASCADE)
    date_of_registration=models.DateField(auto_now_add=True)
    def __str__(self):
        return f'{self.user.email} / {self.published_event.event.name}'
    
    class Meta:
        unique_together = ('user', 'published_event')

class HeldEvent(models.Model):
    published_event=models.ForeignKey(PublishedEvent,on_delete=models.CASCADE)
    number_of_attendees=models.PositiveIntegerField()
    average_rating=models.DecimalField(max_digits=1,decimal_places=1,default=0)

class Attendees(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    held_event=models.ForeignKey(HeldEvent,on_delete=models.CASCADE)
    time=models.DateTimeField(auto_now_add=True)

class Certificate(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    certificate=models.CharField(max_length=255)
