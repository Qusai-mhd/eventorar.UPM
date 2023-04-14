from django import forms

class PublishEventForm(forms.Form):
    OPTIONS = (
        ('all', 'All'),
        ('m', 'Male'),
        ('f', 'Female')
    )
    Target_audience = forms.ChoiceField(choices=OPTIONS)
