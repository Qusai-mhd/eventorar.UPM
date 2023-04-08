from django.contrib import admin
from . import models

# Register your models here.
class PublishedEventAdmin(admin.ModelAdmin):
    readonly_fields = ('date_of_publication',)

admin.site.register(models.PublishedEvent, PublishedEventAdmin)

admin.site.register(models.EndUser)
admin.site.register(models.Event)
admin.site.register(models.HeldEvent)
admin.site.register(models.RegisteredEvent)
admin.site.register(models.Attendees)



