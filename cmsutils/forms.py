from django import forms

from cmsutils.validators import validate_excel_or_csv

# from cmsutils.models import MetaItems


class UploadForm(forms.Form):
    upload_file = forms.FileField(validators=[validate_excel_or_csv])
