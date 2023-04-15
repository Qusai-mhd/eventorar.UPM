from django import forms
from .models import HeldEvent

class PublishEventForm(forms.Form):
    OPTIONS = (
        ('all', 'All'),
        ('m', 'Male'),
        ('f', 'Female')
    )
    Target_audience = forms.ChoiceField(choices=OPTIONS)

class UnpublishEventForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.published_event = kwargs.pop('p_event')
        self.held_event_exists = HeldEvent.objects.filter(published_event=self.published_event).exists()
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.held_event_exists:
            raise forms.ValidationError('Cannot unpublish the event at the moment.')
        return cleaned_data
