# myapp/registry.py

from django.apps import apps
from django.conf import settings


class FieldMappingRegistry:
    def __init__(self):
        self._registry = None  # Lazy load

    def load(self):
        if self._registry is not None:
            return

        config = getattr(settings, "CMSUTILS_MODEL_FIELD_MAP", {})
        self._registry = {}

        for model_label, mapping in config.items():
            model = apps.get_model(*model_label.split("."))

            # Store mapping keyed by model class
            self._registry[model] = mapping

    def get_mapping(self, model):
        self.load()
        return self._registry.get(model)

    def get_value(self, instance, canonical_field):
        self.load()
        model = instance.__class__
        mapping = self._registry.get(model)

        if not mapping:
            raise KeyError(f"No mapping defined for model {model}")

        actual_field = mapping.get(canonical_field)
        if not actual_field:
            raise KeyError(f"No mapping for canonical field '{canonical_field}'")

        return getattr(instance, actual_field)


registry = FieldMappingRegistry()
