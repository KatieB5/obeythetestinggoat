from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
class List(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lists",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="shared_lists",
    )

    def get_absolute_url(self):
        return reverse("view_list", args=[self.id])


    def add(self, email):
        User = get_user_model()
        user = User.objects.get(email=email)
        self.shared_with.add(user)

    @property
    def name(self):
        return self.item_set.first().text


class Item(models.Model):
    text = models.TextField(default="")
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)
        unique_together = ("list", "text")

    def __str__(self):
        return self.text
