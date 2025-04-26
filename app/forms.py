from django import forms

class EventForm(forms.Form):
    title = forms.CharField(max_length=200, required=true)
    description = forms.CharField(widget=forms.Textarea, required=True)
    scheduled_at = forms.DateTimeField(required=True)

def clean(self):
    cleaned_data = super(),clean()
    title = cleaned_data.get('title')
    description = cleaned_data.get('description')
    scheduled_at = cleaned_data.get('scheduled_at')

    from .models import Event
    errors = Event.validate(title, description, scheduled_at)

    if errors:
        for field, error in errors.items():
            self.add_error(field, error)
    
    return cleaned_data