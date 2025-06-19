from django.db import models
from case.models import Case


class CaseNote(models.Model):

    case = models.ForeignKey(Case, related_name='notes',
                             on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)

    claim = models.TextField(blank=True, null=True)
    claim_title = models.CharField(max_length=255, blank=True, null=True)
    claim_text = models.TextField(blank=True, null=True)

    attachment_file_name = models.CharField(
        max_length=255, blank=True, null=True)
    attachment_file_type = models.CharField(
        max_length=100, blank=True, null=True)
    attachment_url = models.URLField(blank=True, null=True)
    attachment_created_at = models.DateTimeField(blank=True, null=True)
    is_judgement_note = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
