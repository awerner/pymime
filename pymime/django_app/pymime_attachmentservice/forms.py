from django import forms

class ReportForm(forms.Form):
    reason = forms.CharField(label="message", widget=forms.Textarea)
    reporter_mail = forms.EmailField(label="your email")
