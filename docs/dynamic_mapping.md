# Mapping fields dynamically

```
# settings.py

MODEL_FIELD_MAP = {
    "pages.Page": {
        "title": "title",
        "description": "description",
    },
    "news.models.NewsArticle": {
        "title": "title",
        "description": "body",
    },
    "events.models.Event": {
        "title": "name",
        "description": "description",
    },
}

```
