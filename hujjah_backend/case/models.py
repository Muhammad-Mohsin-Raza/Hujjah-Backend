from django.db import models
from client.models import Client  # assuming you already have this


class Case(models.Model):

    client = models.ForeignKey(
        Client, related_name='cases', on_delete=models.CASCADE)
    case_name = models.CharField(max_length=255, blank=True, null=True)
    closed = models.BooleanField(default=False)
    closing_info = models.TextField(blank=True, null=True)
    closing_info_status = models.CharField(
        max_length=50, blank=True, null=True)
    closing_info_percentage = models.CharField(
        max_length=10, blank=True, null=True)
    my_case_note = models.TextField(blank=True, null=True)
    my_case_note_updated = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.case_name or f"Case #{self.pk}"
