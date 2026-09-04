# admin.py
from django.contrib import admin, messages

# from cmsutils.views import approved_list_view
from django.db.models import ObjectDoesNotExist
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from filer.models import Image

from cmsutils.forms import UploadForm
from cmsutils.models import ImageUpdates, PageUpdates
from cmsutils.utils import get_object_from_url, parse_uploaded_file


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

    list_display = (
        "page_url",
        # "failed_warning",
        "title",
        "description",
        "approved_at",
        "approved_user",
    )

    list_filter = ("approved_user", NoDateFilter)

    change_list_template = "admin/cmsutils/pageupdates_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload),
                name="pageupdates_upload",
            ),
        ]
        return custom_urls + urls

    def upload(self, request):
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data["upload_file"]

                try:
                    rows = parse_uploaded_file(file)
                except ValueError as e:
                    self.message_user(request, str(e), level="error")
                    return redirect("admin:cmsutils_pageupdates_changelist")

                for row in rows:
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
            form = UploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/upload.html", context)

    @admin.action(description="Update selected pages", permissions=["change"])
    def update_pages(self, request, queryset):
        """
        Iterate over selected PageUpdates objects, find the corresponding page
        object or related model via the URL (using cmsutils.utils.get_object_from_url),
        and update the title and description fields using cmsutils.registry.registry.get_value()
        method to retrieve the correct field names based on the model's mapping.

        If the page cannot be found, mark it as failed.
        """

        fails = 0

        for obj in queryset:
            try:
                o = get_object_from_url(obj.url)
            except ObjectDoesNotExist:
                o = None

            # we didn't get a match for the URL, so we can't update anything
            if not o:
                fails += 1
                obj.failed_at = timezone.now()
                obj.save()
                continue

            if o["type"] == "cms_page":

                # could possibly condense the logic to use the same function for both cms_page and apphook types,
                # but for now, keep them separate for clarity

                # check the status of the page before updating
                if o["object"].status == 2:  # 2 is the status for "published"
                    o["object"].title = obj.title
                    o["object"].description = obj.description
                    o["object"].save()

                    obj.approved_user = request.user
                    obj.approved_at = timezone.now()
                    obj.save()
                else:
                    fails += 1
                    obj.failed_at = timezone.now()
                    obj.save()

            elif o["type"] == "apphook":
                # TODO pull in the registry mapping logic here to update the page title and description

                # do apphook update logic here if needed
                obj.approved_user = request.user
                obj.approved_at = timezone.now()
                obj.save()

            else:
                fails += 1
                obj.failed_at = timezone.now()
                obj.save()

        self.message_user(
            request,
            f"{queryset.count() - fails} page(s) have been updated. {fails} page(s) could not be found.",
            messages.SUCCESS,
        )


    actions = ["update_pages"]


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
                "upload/",
                self.admin_site.admin_view(self.upload),
                name="imageupdates_upload",
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

    def upload(self, request):
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data["upload_file"]

                try:
                    rows = parse_uploaded_file(file)
                except ValueError as e:
                    self.message_user(request, str(e), level="error")
                    return redirect("admin:cmsutils_imageupdates_changelist")

                for row in rows:
                    temp_object = {
                        "image_url": row.get("image_url", ""),
                        "image_alt_text": row.get("image_alt_text", ""),
                        "upload_user": request.user,
                    }

                    ImageUpdates.objects.create(**temp_object)

                self.message_user(request, "Upload complete.")
                return redirect("admin:cmsutils_imageupdates_changelist")
        else:
            form = UploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/upload.html", context)

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
