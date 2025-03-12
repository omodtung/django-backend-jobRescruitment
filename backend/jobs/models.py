from django.db import models
from companies.models import Company

class Job(models.Model):
    """
    Represents the Job entity.
    """
    name = models.CharField(max_length=255)  # Job name/title
    skill = models.JSONField(blank=True, null=True)  # Skills required, stored as a list in JSON
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')  # The company offering the job
    location = models.CharField(max_length=255, blank=True, null=True)  # Location of the job
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Salary for the job
    quantity = models.CharField(max_length=255, blank=True, null=True)  # Number of positions available
    level = models.CharField(max_length=255, blank=True, null=True)  # Job level (e.g., Entry, Mid, Senior)
    description = models.TextField(blank=True, null=True)  # Description of the job

    start_date = models.DateField(blank=True, null=True)  # Job starting date
    end_date = models.DateField(blank=True, null=True)  # Job ending date

    is_active = models.BooleanField(default=True)  # Whether the job is currently active

    created_by = models.JSONField(blank=True, null=True)  # Creator details as JSON
    updated_by = models.JSONField(blank=True, null=True)  # Updator details as JSON
    deleted_by = models.JSONField(blank=True, null=True)  # Deletor details as JSON

    is_deleted = models.BooleanField(default=False)  # Whether the job is marked as deleted
    deleted_at = models.DateTimeField(blank=True, null=True)  # Timestamp for when the job was deleted

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update

    def __str__(self):
        return self.name