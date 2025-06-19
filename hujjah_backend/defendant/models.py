from django.db import models
from case.models import Case

# Create your models here.


class Defendant(models.Model):

    case = models.OneToOneField(
        Case, related_name='defendant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    national_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    commercial_register = models.CharField(
        max_length=100, blank=True, null=True)
    nature_of_activity = models.CharField(
        max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    national_address = models.TextField(blank=True, null=True)

    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    iban_number = models.CharField(max_length=100, blank=True, null=True)

    additional_mobile_number = models.CharField(
        max_length=20, blank=True, null=True)
    current_profession = models.CharField(
        max_length=100, blank=True, null=True)
    employer = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
