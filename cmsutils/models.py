from django.db import models


class TitleDescriptionUpdates(models.Model):
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
        related_name="title_description_upload_user",
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="title_description_approved_user",
    )

    # class Meta:
    #     abstract = True
