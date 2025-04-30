from django import forms
from .models import Comment

class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'content']
        widgets = {
            'title' : forms.TextInput(attrs={'placeholder':'Titulo del comentario...'}),
            'content' : forms.Textarea(attrs={'placeholder' : 'Escribe tu comentario...'}),
        }