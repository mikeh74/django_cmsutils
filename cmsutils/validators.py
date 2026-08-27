import yaml
from django.core.exceptions import ValidationError


def validate_yaml(value):
    """Validates Yaml for use in model validation

    Takes a string and checks whether it is valid yaml or not

    Args:
      value: string to validate

    Raises:
      ValidationError
    """

    is_valid = True
    msg = ""

    if value:
        try:
            is_valid = yaml.safe_load(value)
        except Exception as e:
            is_valid = False
            msg = e

    if is_valid is False:
        raise ValidationError(
            "YAML parsing error: {}".format(msg), params={"value": value}
        )

def validate_excel_or_csv(file):
    """Validates that the uploaded file is either an Excel or CSV file.

    Args:
        file: The uploaded file to validate.

    Raises:
        ValidationError: If the uploaded file is not an Excel or CSV file.
    """
    valid_mime_types = [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
    ]
    valid_extensions = [".xls", ".xlsx", ".csv"]

    file_mime_type = file.content_type
    file_extension = file.name.split(".")[-1].lower()

    if file_mime_type not in valid_mime_types or f".{file_extension}" not in valid_extensions:
        raise ValidationError(
            "Invalid file type. Please upload an Excel (.xls, .xlsx) or CSV (.csv) file."
        )
