from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class EndUser(AbstractUser):
    email=models.EmailField(unique=True)

class Event(models.Model):
    name=models.CharField(max_length=255)
    organizer=models.CharField(max_length=255,null=True,blank=True)
    date=models.DateField()
    time=models.TimeField()
    location=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)

    def __str__(self) -> str:
        return self.name
    class Meta:
        ordering=['date']

class PublishedEvent(models.Model):
    event_id=models.ForeignKey(Event,on_delete=models.CASCADE)
    date_of_publication=models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.event_id.name
    class Meta:
        ordering=['date_of_publication']
    
class RegisteredEvent(models.Model):
    user_id=models.ForeignKey(EndUser,on_delete=models.CASCADE)
    event_id=models.ForeignKey(PublishedEvent,on_delete=models.CASCADE)

class HeldEvent(models.Model):
    event_id=models.ForeignKey(EndUser,on_delete=models.CASCADE)
    number_of_attendees=models.PositiveIntegerField()
    average_rating=models.DecimalField(max_digits=1,decimal_places=1,default=0)

class Attendees(models.Model):
    user_id=models.ForeignKey(EndUser,on_delete=models.CASCADE)
    event_id=models.ForeignKey(HeldEvent,on_delete=models.CASCADE)
    time=models.DateTimeField(auto_now_add=True)

class Certificate(models.Model):
    user_id=models.ForeignKey(EndUser,on_delete=models.PROTECT)
    certificate=models.CharField(max_length=255)
