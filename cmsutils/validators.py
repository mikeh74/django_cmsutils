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
