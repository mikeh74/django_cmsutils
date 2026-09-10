import csv
import os
from urllib.parse import urlsplit

import pandas as pd  # handles both .xls and .xlsx cleanly
from cms.apphook_pool import apphook_pool
from cms.appresolver import applications_page_check
from cms.utils.page import get_page_from_request
from django.test import RequestFactory
from django.urls import Resolver404, resolve

from cmsutils.registry import registry


def parse_uploaded_file(file):
    name = file.name.lower()
    ext = os.path.splitext(name)[1]

    if ext == ".csv":
        decoded = file.read().decode("utf-8").splitlines()
        return list(csv.DictReader(decoded))

    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file)
        return df.to_dict(orient="records")

    else:
        raise ValueError("Unsupported file type")


def get_object_from_url(url):
    """
    Given a URL, returns the corresponding model instance if it exists.
    Returns None if the URL does not correspond to a valid page or apphook.

    Returns a dictionary with the following keys:
    - type: "cms_page", "apphook", or "not_found"
    - page: The CMS page object if type is "cms_page" or "apphook", else None
    - apphook: The apphook name if type is "apphook", else None
    - view: The view function if type is "apphook", else None
    - model_instance: The model instance if type is "apphook", else None
    - object: The resolved object (page or model instance) if found, else None

    """
    request = _build_temp_request(url)
    return _resolve_cms_or_apphook(request)


def _build_temp_request(raw_url):
    parts = urlsplit(raw_url)
    path = parts.path or "/"
    query = parts.query

    factory = RequestFactory()
    request = factory.get(path + (f"?{query}" if query else ""))

    request.LANGUAGE_CODE = "en"
    return request


def _resolve_cms_or_apphook(request):
    """
    Takes a request object and returns a dictionary with information about
    the resolved page, apphook, view, and model instance.
    """

    page = get_page_from_request(request)

    if not page:
        # Apphook subpaths usually do not match cms.PageUrl directly.
        page = applications_page_check(request)

    if page and not page.application_urls:
        return {
            "type": "cms_page",
            "page": page,
            "apphook": None,
            "apphook_instance": None,
            "apphook_config": None,
            "view": None,
            "model_instance": None,
            "object": page,
        }

    if page and page.application_urls:
        apphook_name = page.application_urls
        apphook_instance = apphook_pool.get_apphook(apphook_name)

        apphook_config = None
        if apphook_instance and getattr(apphook_instance, "app_config", None) and page.application_namespace:
            try:
                apphook_config = apphook_instance.get_config(page.application_namespace)
            except Exception:
                apphook_config = None

        match = None
        model_instance = None

        try:
            match = resolve(request.path_info)
        except Resolver404:
            pass

        if match and hasattr(match.func, "view_class"):
            view = match.func.view_class()
            view.request = request
            view.args = match.args
            view.kwargs = match.kwargs
            if hasattr(view, "get_object"):
                try:
                    model_instance = view.get_object()
                except Exception:
                    model_instance = None

        return {
            "type": "apphook",
            "page": page,
            "apphook": apphook_name,
            "apphook_instance": apphook_instance,
            "apphook_config": apphook_config,
            "view": match.func if match else None,
            "model_instance": model_instance,
            "object": model_instance,
        }

    return {
        "type": "not_found",
        "page": None,
        "apphook": None,
        "apphook_instance": None,
        "apphook_config": None,
        "view": None,
        "model_instance": None,
        "object": None,
    }


def update_field_from_map(instance, data: dict):
    """
    Update the fields of a model instance based on a mapping defined in the registry.
    """
    mapping = registry.get_mapping(instance.__class__)
    if not mapping:
        raise KeyError(f"No mapping defined for model {instance.__class__}")

    for field, value in data.items():
        actual_field = mapping.get(field)
        if not actual_field:
            continue  # ignore unknown fields

        setattr(instance, actual_field, value)

    instance.save()
    return instance
