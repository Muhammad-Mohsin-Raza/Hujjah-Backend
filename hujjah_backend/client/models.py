from django.db import models
from django.conf import settings

class Client(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # This ensures it uses your custom User model
        on_delete=models.CASCADE,
        related_name='clients',
        blank=True
    )
    customer_name = models.CharField(max_length=255)
    agency_number = models.CharField(max_length=100)
    agency_history = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    agency_date = models.DateField(blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    total_due = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    

    # Additional optional fields
    national_id = models.CharField(max_length=50, blank=True, null=True)
    commercial_register = models.CharField(max_length=100, blank=True, null=True)
    nature_of_activity = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    national_address = models.TextField(blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    iban_number = models.CharField(max_length=34, blank=True, null=True)
    additional_mobile_number = models.CharField(max_length=20, blank=True, null=True)
    current_profession = models.CharField(max_length=100, blank=True, null=True)
    employer = models.CharField(max_length=100, blank=True, null=True)
    gender=models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #From ai page fields
    region = models.CharField(max_length=100, null=True)


    def __str__(self):
        return f"{self.customer_name} - {self.agency_number}"
