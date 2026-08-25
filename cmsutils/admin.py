# admin.py
import csv

from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path

from cmsutils.forms import CSVUploadForm
from cmsutils.models import ImageUpdates, PageUpdates


@admin.register(PageUpdates)
class PageUpdatesAdmin(admin.ModelAdmin):
    exclude = (
        "model_name",
        "model_id",
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



@admin.register(ImageUpdates)
class ImageUpdatesAdmin(admin.ModelAdmin):
    exclude = (
        "model_name",
        "model_id",
        "upload_user",
        "approved_at",
        "approved_user",
    )

    change_list_template = "admin/cmsutils/imageupdates_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_csv),
                name="imageupdates_upload_csv",
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
                        "image_url": row.get("url", ""),
                        "image_alt_text": row.get("alt_text", ""),
                        "image_id": row.get("id", ""),
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
