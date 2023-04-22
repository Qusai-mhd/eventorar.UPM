from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PublishedEvent

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PublishedEvent, HeldEvent,Attendees

@receiver(post_save, sender=PublishedEvent)
def create_held_event_if_time_passed(sender, instance, created, **kwargs):
    if created:
        return  # ignore updates to existing PublishedEvent instances

    for published_event in PublishedEvent.objects.filter(is_held=False):
        if published_event.event.date < timezone.now().date():
            # check if a HeldEvent instance already exists for this published event
            if not HeldEvent.objects.filter(published_event=published_event).exists():
                HeldEvent.objects.create(published_event=published_event, number_of_attendees=0)
                published_event.is_held=True
                published_event.save()


@receiver(post_save, sender=Attendees)
def create_held_event_if_attendee_added(sender, instance, created, **kwargs):
    if created:
        held_event = HeldEvent.objects.get(id=instance.held_event.id)
        held_event.number_of_attendees += 1
        held_event.save()



# @receiver(post_save, sender=Attendees)
# def create_held_event_if_attendee_added(sender, instance, created, **kwargs):
#     if created:
#         published_event = instance.held_event.published_event
#         if not HeldEvent.objects.filter(published_event=published_event).exists():
#             held_event = HeldEvent.objects.create(published_event=published_event, number_of_attendees=1)
#             published_event.is_held = True
#             published_event.save()
#         else:
#             held_event = HeldEvent.objects.get(published_event=published_event)
#             held_event.number_of_attendees += 1
#             held_event.save()