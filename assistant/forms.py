from django import forms


class CreateThreadForm(forms.Form):
    initial_message = forms.Textarea()
