from .models import Comment
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Event, Venue
from .models import Category


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'scheduled_at', 'venue']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'venue': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['venue'].queryset = Venue.objects.filter(
                created_by=self.user)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 5:
            raise ValidationError(
                "El título debe tener al menos 5 caracteres.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 20:
            raise ValidationError(
                "La descripción debe tener al menos 20 caracteres.")
        return description

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data.get('scheduled_at')
        if scheduled_at and scheduled_at < timezone.now():
            raise ValidationError("La fecha/hora debe ser futura.")
        return scheduled_at


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("El nombre es obligatorio.")
        # Puedes agregar más validaciones si es necesario
        return name


class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Titulo del comentario...'}),
            'content': forms.Textarea(attrs={'placeholder': 'Escribe tu comentario...'}),
        }
