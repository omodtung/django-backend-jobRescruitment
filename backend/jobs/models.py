from django.db import models
from companies.models import Companies
from datetime import datetime, timezone
from django.contrib.postgres.fields import ArrayField  # ✅ Import đúng

class Job(models.Model):
    """
    Represents the Job entity.
    """
    name = models.CharField(max_length=255)  # Job name/title
    skills = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )  # Skills required, stored as a list in JSON
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='jobs')  # The company offering the job
    location = models.CharField(max_length=255, blank=True, null=True)  # Location of the job
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Salary for the job
    quantity = models.CharField(max_length=255, blank=True, null=True)  # Number of positions available
    level = models.CharField(max_length=255, blank=True, null=True)  # Job level (e.g., Entry, Mid, Senior)
    description = models.TextField(blank=True, null=True)  # Description of the job

    start_date = models.DateTimeField(blank=True, null=True)  # Job starting date
    end_date = models.DateTimeField(blank=True, null=True)  # Job ending date

    is_active = models.BooleanField(default=True)  # Whether the job is currently active

    created_by = models.JSONField(blank=True, null=True)  # Creator details as JSON
    updated_by = models.JSONField(blank=True, null=True)  # Updator details as JSON
    deleted_by = models.JSONField(blank=True, null=True)  # Deletor details as JSON

    is_deleted = models.BooleanField(default=False)  # Whether the job is marked as deleted
    deleted_at = models.DateTimeField(blank=True, null=True)  # Timestamp for when the job was deleted

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update

    def soft_delete(self, deleted_by=None):
        now = datetime.now(timezone.utc)  # lấy thời gian UTC hiện tại
        self.is_deleted = True
        self.deleted_at = now
        if deleted_by:
            self.deleted_by = deleted_by
        self.save()

    def delete(self, *args, **kwargs):
        self.soft_delete()

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "jobs"