# admin.py
import csv

from django.contrib import admin, messages

# from cmsutils.views import approved_list_view
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from django.utils import timezone
from filer.models import Image, format_html

from cmsutils.forms import CSVUploadForm
from cmsutils.models import ImageUpdates, PageUpdates


@admin.register(PageUpdates)
class PageUpdatesAdmin(admin.ModelAdmin):
    exclude = (
        "model_name",
        "model_id",
        # "upload_user",
        "approved_at",
        "approved_user",
    )

    readonly_fields = (
        "page_url",
        "upload_user",
        "approved_at",
        "approved_user",
    )

    change_list_template = "admin/cmsutils/pageupdates_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_csv),
                name="pageupdates_upload_csv",
            ),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data["csv_file"]
                decoded = file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded)

                for row in reader:
                    temp_object = {
                        "page_url": row.get("url", ""),
                        "title": row.get("title", ""),
                        "description": row.get("description", ""),
                        "upload_user": request.user,
                    }

                    PageUpdates.objects.create(**temp_object)

                self.message_user(request, "Upload complete.")
                return redirect("admin:cmsutils_pageupdates_changelist")
        else:
            form = CSVUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/upload_csv.html", context)


class NoDateFilter(admin.SimpleListFilter):
    title = "Date status"
    parameter_name = "date_status"

    def lookups(self, request, model_admin):
        return [
            ("none", "Not updated"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(approved_at__isnull=True)
        return queryset


@admin.register(ImageUpdates)
class ImageUpdatesAdmin(admin.ModelAdmin):
    exclude = (
        "model_name",
        "model_id",
        "upload_user",
        "approved_at",
        "approved_user",
    )

    readonly_fields = (
        "image_url",
        "image_filename",
        "upload_user",
        "created_at",
        "approved_at",
        "approved_user",
    )

    list_display = (
        "image_filename",
        "failed_warning",
        "image_alt_text",
        "approved_at",
        "approved_user",
        "image_url",
    )
    list_filter = ("approved_user", NoDateFilter)

    def failed_warning(self, obj):
        if obj.failed_at is not None:
            return format_html(
                '<span title="Failed to update {}." style="color:#d97706;">⚠️</span>',
                obj.failed_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        return ""

    failed_warning.short_description = "Failed"

    change_list_template = "admin/cmsutils/imageupdates_changelist.html"

    def get_queryset(self, request):

        qs = super().get_queryset(request)
        # Detect which view is being rendered
        url_name = request.resolver_match.url_name

        if url_name == "cmsutils_imageupdates_changelist":
            # Main changelist
            return qs.filter(approved_at__isnull=True)

        if url_name == "imageupdates_approved_list":
            # Your custom alternate view
            return qs.filter(approved_at__isnull=False)

        # Fallback (e.g., rejected list, pending list, etc.)
        return qs

    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of ImageUpdates objects that have been approved."""
        if obj:
            return bool(not obj.approved_at)
        return True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_csv),
                name="imageupdates_upload_csv",
            ),
            path(
                "approved-list/",
                self.admin_site.admin_view(self.approved_list_view),
                name="imageupdates_approved_list",
            ),
        ]
        return custom_urls + urls

    def approved_list_view(self, request):
        # Clone the request so we don't mutate the original
        original_request = request
        request = HttpRequest()
        request.__dict__.update(original_request.__dict__)

        # Call the normal changelist view
        response = self.changelist_view(request)
        response.context_data["title"] = "Approved Image Update Audit List"
        return response

    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data["csv_file"]
                decoded = file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded)

                for row in reader:
                    temp_object = {
                        "image_url": row.get("image_url", ""),
                        "image_alt_text": row.get("image_alt_text", ""),
                        "upload_user": request.user,
                    }

                    ImageUpdates.objects.create(**temp_object)

                self.message_user(request, "Upload complete.")
                return redirect("admin:cmsutils_imageupdates_changelist")
        else:
            form = CSVUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/upload_csv.html", context)

    actions = ["update_images"]

    @admin.action(description="Update selected images", permissions=["change"])
    def update_images(self, request, queryset):

        fails = 0

        for obj in queryset:
            try:
                # Attempt to retrieve the image object from the database using the normalized URL
                # File.objects.get(url=normalized_url)
                # i = Image.objects.get(id=File.objects.get(url=normalized_url).id)
                img = Image.objects.filter(file=obj.normalized_image_url).first()
            except Image.DoesNotExist:
                img = None

            if img:
                img.default_alt_text = obj.image_alt_text
                img.save()

                obj.approved_user = request.user
                obj.approved_at = timezone.now()
                obj.save()
            else:
                fails += 1
                obj.failed_at = timezone.now()
                obj.save()

        self.message_user(
            request,
            f"{queryset.count() - fails} image(s) have had alt_text updated. {fails} image(s) could not be found.",
            messages.SUCCESS,
        )
