from django import forms

from cmsutils.validators import validate_excel_or_csv

# from cmsutils.models import MetaItems


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(validators=[validate_excel_or_csv])
