# admin.py
import csv

from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path

from cmsutils.forms import CSVUploadForm
from cmsutils.models import TitleDescriptionUpdates


@admin.register(TitleDescriptionUpdates)
class TitleDescriptionUpdatesAdmin(admin.ModelAdmin):
    change_list_template = "admin/cmsutils/titledescriptionupdates_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_csv),
                name="titledescriptionupdates_upload_csv",
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
                    TitleDescriptionUpdates.objects.create(**row)

                self.message_user(request, "Upload complete.")
                return redirect("admin:cmsutils_titledescriptionupdates_changelist")
        else:
            form = CSVUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/upload_csv.html", context)
