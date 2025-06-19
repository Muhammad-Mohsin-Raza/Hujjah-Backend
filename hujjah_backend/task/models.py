# task/models.py

from django.db import models
from case.models import Case
from client.models import Client


class Task(models.Model):
    """
    Task model represents a task related to a case.

    Fields:
    - title: Title of the task.
    - description: Detailed description of the task.
    - due_date: Deadline for the task.
    - priority: Priority level (Arabic enums): 'عالية' (High), 'متوسطة' (Medium), 'منخفضة' (Low).
    - status: Task status (Arabic enums): 'جديدة' (New), 'قيد التنفيذ' (In Progress), 'مكتملة' (Completed).
    - case: ForeignKey to related Case.
    """

    PRIORITY_CHOICES = [
        ('عالية', 'عالية'),
        ('متوسطة', 'متوسطة'),
        ('منخفضة', 'منخفضة'),
    ]

    STATUS_CHOICES = [
        ('جديدة', 'جديدة'),
        ('قيد التنفيذ', 'قيد التنفيذ'),
        ('مكتملة', 'مكتملة'),
        ('ملغاة', 'ملغاة'),
    ]

    client = models.ForeignKey(Client, related_name='tasks',
                               on_delete=models.CASCADE, null=True,  # Allow NULLs in DB
                               blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Arabic Task Enums - Translations for reference:
#
# PRIORITY:
# "عالية"     => "High"
# "متوسطة"   => "Medium"
# "منخفضة"   => "Low"
#
# STATUS:
# "جديدة"        => "New"
# "قيد التنفيذ"  => "In Progress"
# "مكتملة"       => "Completed"
#
# These enums are stored/displayed in Arabic for localization purposes.
# Use the translations above to understand or process them in your backend logic.
