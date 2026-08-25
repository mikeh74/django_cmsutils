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
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="image_updates_approved_user",
    )

    def get_image_filename(self):
        if self.image_url:
            return self.image_url.split("/")[-1]
        return None

    def __str__(self):
        return f"{self.image_alt_text} ({self.get_image_filename()})"

    class Meta:
        verbose_name = "Image Update"
        verbose_name_plural = "Image Updates"
