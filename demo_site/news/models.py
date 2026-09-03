from django.db import models


# Create your models here.
class News(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("news:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name
