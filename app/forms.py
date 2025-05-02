from django import forms
from .models import RefundRequest

class RefundRequestForm(forms.ModelForm):
    accept_policy = forms.BooleanField(
        label="Acepto la política de reembolsos",
        required=True
    )

    class Meta:
        model = RefundRequest
        fields = ['reason', 'policy_30_days']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Proporciona más información...'})
        }