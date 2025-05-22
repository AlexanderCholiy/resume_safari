from django import forms


class BirthdayForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    birthday = forms.DateField()
