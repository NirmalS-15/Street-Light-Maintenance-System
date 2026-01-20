# complaints/forms.py
from django import forms
from .models import ComplaintReply

class ComplaintReplyForm(forms.ModelForm):
    class Meta:
        model = ComplaintReply
        fields = ['message', 'photo']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message to the user...'}),
        }