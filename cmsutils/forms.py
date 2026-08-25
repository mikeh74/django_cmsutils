from django import forms

# from cmsutils.models import MetaItems


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
