# Dynamic Django Model Mapping & Registry — Conversation Summary

## 1. Representing Django Models as Strings

You cannot use strings directly with `isinstance()`, because `isinstance()` requires a **class**, not a string.  
Instead, store model identifiers as strings and resolve them dynamically.

### Recommended identifiers
- `app_label.ModelName` → works with `apps.get_model`
- `myapp.models.MyModel` → works with `import_string`

### Resolve string → class

```python
from django.apps import apps
ModelClass = apps.get_model("myapp.MyModel")
```

or

```python
from django.utils.module_loading import import_string
ModelClass = import_string("myapp.models.MyModel")
```

---

## 2. Dynamic Metadata Between Unrelated Apps

You can store metadata in `settings.py` and dynamically resolve it at runtime.  
This allows unrelated apps to interact without direct imports.

### Example settings structure

```python
MY_DYNAMIC_MODEL_MAP = {
    "billing.Customer": {
        "serializer": "billing.serializers.CustomerSerializer",
        "permissions": ["view_customer", "change_customer"],
        "related_handler": "integration.handlers.customer_handler",
    },
    "inventory.Product": {
        "serializer": "inventory.serializers.ProductSerializer",
        "permissions": ["view_product"],
        "related_handler": "integration.handlers.product_handler",
    },
}
```

---

## 3. Dynamic Registry Pattern

A registry loads metadata once and exposes fast lookups.

### Registry implementation

```python
from django.apps import apps
from django.utils.module_loading import import_string
from django.conf import settings

class DynamicModelRegistry:
    def __init__(self):
        self._registry = {}

    def load(self):
        for model_label, meta in settings.MY_DYNAMIC_MODEL_MAP.items():
            model = apps.get_model(*model_label.split("."))

            serializer = import_string(meta["serializer"])
            handler = import_string(meta["related_handler"])

            self._registry[model] = {
                "serializer": serializer,
                "permissions": meta.get("permissions", []),
                "handler": handler,
            }

    def get(self, model):
        return self._registry.get(model)

registry = DynamicModelRegistry()
```

---

## 4. Initializing Registry in `AppConfig.ready()`

```python
# myapp/apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = "myapp"

    def ready(self):
        from .registry import registry
        registry.load()
```

---

## 5. Initializing Registry at Module Import (Lazy)

```python
# myapp/registry.py

class DynamicModelRegistry:
    def __init__(self):
        self._registry = None

    def load(self):
        if self._registry is not None:
            return

        config = settings.MY_DYNAMIC_MODEL_MAP
        self._registry = {}

        for model_label, meta in config.items():
            model = apps.get_model(*model_label.split("."))
            serializer = import_string(meta["serializer"])
            handler = import_string(meta["related_handler"])
            self._registry[model] = meta

    def get(self, model):
        self.load()
        return self._registry.get(model)

registry = DynamicModelRegistry()
```

---

## 6. Field Mapping Between Different Models

### Settings example

```python
MODEL_FIELD_MAP = {
    "pages.Page": {
        "title": "title",
        "description": "description",
    },
    "news.NewsArticle": {
        "title": "title",
        "description": "body",
    },
    "events.Event": {
        "title": "name",
        "description": "description",
    },
}
```

---

## 7. Registry for Field Mapping

```python
class FieldMappingRegistry:
    def __init__(self):
        self._registry = None

    def load(self):
        if self._registry is not None:
            return

        config = getattr(settings, "CMSUTILS_MODEL_FIELD_MAP", None)
        self._registry = {}

        for model_label, mapping in config.items():
            model = apps.get_model(*model_label.split("."))
            self._registry[model] = mapping

    def get_mapping(self, model):
        self.load()
        return self._registry.get(model)

registry = FieldMappingRegistry()
```

---

## 8. Updating Any Model Using Canonical Fields

```python
def update_from_canonical(instance, data):
    mapping = registry.get_mapping(instance.__class__)
    if not mapping:
        raise KeyError(f"No mapping defined for model {instance.__class__}")

    for canonical_field, value in data.items():
        actual_field = mapping.get(canonical_field)
        if actual_field:
            setattr(instance, actual_field, value)

    instance.save()
    return instance
```

---

## 9. Adding Validation to Field Mapping

### Validate mapping at startup

```python
from django.core.exceptions import FieldDoesNotExist

class FieldMappingRegistry:
    def __init__(self):
        self._registry = None
        self._canonical_fields = set()

    def load(self):
        if self._registry is not None:
            return

        config = settings.MODEL_FIELD_MAP
        self._registry = {}

        for model_label, mapping in config.items():
            model = apps.get_model(*model_label.split("."))

            for canonical, actual in mapping.items():
                self._canonical_fields.add(canonical)

                try:
                    model._meta.get_field(actual)
                except FieldDoesNotExist:
                    raise ValueError(
                        f"Invalid mapping: '{actual}' is not a field on {model_label}"
                    )

            self._registry[model] = mapping

    def validate_update_data(self, data):
        unknown = set(data.keys()) - self._canonical_fields
        if unknown:
            raise ValueError(f"Unknown canonical fields: {', '.join(unknown)}")

registry = FieldMappingRegistry()
```

---

## 10. Validated Update Function

```python
def update_from_canonical(instance, data):
    registry.validate_update_data(data)

    mapping = registry.get_mapping(instance.__class__)
    if not mapping:
        raise KeyError(f"No mapping defined for model {instance.__class__}")

    for canonical_field, value in data.items():
        actual_field = mapping.get(canonical_field)
        if actual_field:
            setattr(instance, actual_field, value)

    instance.save()
    return instance
```

---

## 11. What This Architecture Gives You

- A single update API for many model types  
- No cross‑app imports  
- Schema validation at startup  
- Safe canonical field vocabulary  
- Extensible mapping system  
- Zero meaningful runtime overhead  

---

If you want, I can also produce:

- A **bi‑directional mapping** (canonical → model, model → canonical)  
- A **canonical serializer**  
- A **relationship mapping system**  
- A **full integration layer** between apps  

Just tell me which direction you want to expand.