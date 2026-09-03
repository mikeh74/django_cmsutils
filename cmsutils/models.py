from urllib.parse import urlsplit

from django.conf import settings
from django.db import models


class PageUpdates(models.Model):
    page_url = models.URLField(blank=True, null=True)
    model_name = models.CharField(max_length=255, blank=True, null=True)
    model_id = models.PositiveIntegerField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upload_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="page_updates_upload_user",
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="page_updates_approved_user",
    )

    def __str__(self):
        return f"{self.title} ({self.page_url})"

    class Meta:
        verbose_name = "Page Update"
        verbose_name_plural = "Page Updates"


class ImageUpdates(models.Model):
    image_url = models.URLField(blank=True, null=True)
    image_alt_text = models.CharField(max_length=255, blank=True, null=True)
    image_id = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upload_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="image_updates_upload_user",
    )
    approved_at = models.DateTimeField("Approved at", blank=True, null=True)
    approved_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="image_updates_approved_user",
        verbose_name="Approved by",
    )
    failed_at = models.DateTimeField(
        "Failed at",
        blank=True,
        null=True,
    )

    @property
    def image_filename(self):
        if self.image_url:
            parsed_url = urlsplit(self.image_url)
            return parsed_url.path.split("/")[-1].split("__")[
                0
            ]  # Get the last part of the path and remove thumbnail suffix
        return None

    @property
    def normalized_image_url(self):
        """
        Returns the normalized image URL by removing the domain and media URL prefix.
        It also handles thumbnail URLs by removing the thumbnail prefix and suffix to get the original image URL.

        TODO: Consider using a more robust URL parsing method to handle edge cases and different URL formats.
        Should we parse and normalize the URL on imporrt, using urllib.parse or a similar library to ensure we handle all possible URL formats correctly?

        """

        if not self.image_url:
            return None

        parsed_url = urlsplit(self.image_url)

        if not parsed_url.path:
            return None

        normalized_url = parsed_url.path.strip().lower()

        media_url = settings.MEDIA_URL

        # strip the media_url prefix if it exists
        if normalized_url.startswith(f"{media_url}"):
            normalized_url = normalized_url[len(media_url) :]

        # is it a thumbnail?
        # if it is then rewrite to remove filer_public_thumbnails and the thumbnail suffix
        if normalized_url.startswith("filer_public_thumbnails/"):
            # Remove the thumbnail prefix and suffix to get the original image URL
            normalized_url = normalized_url.replace("filer_public_thumbnails/", "")
            # Remove the thumbnail suffix (e.g., __40x40_q85_crop_subsampling-2.jpg)
            normalized_url = normalized_url.split("__")[0]
        return normalized_url

    def __str__(self):
        return f"{self.image_alt_text} ({self.image_filename})"

    class Meta:
        verbose_name = "Image Update"
        verbose_name_plural = "Image Updates"
