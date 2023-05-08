from django import forms

from .models import ConsentRequest


class ConsentRequestForm(forms.ModelForm):

    class Meta:
        model = ConsentRequest
        fields = ['patientid', 'requestedrole']
