from django.db import models
from django.utils.timezone import now
from companies.models import Companies
from jobs.models import Job 
class Resume(models.Model):
    email = models.EmailField(max_length=255)
    user_id = models.CharField(max_length=24)
    company = models.ForeignKey(
        Companies,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    job= models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    history = models.JSONField(default=list, blank=True)
    url = models.URLField(max_length=200, blank=True)
    status = models.CharField(max_length=50, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.JSONField(default=dict, blank=True)
    updated_by = models.JSONField(default=dict, blank=True)
    delete_by = models.JSONField(default=dict, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.email

# Create your models here.
    class Meta:
        db_table = "resume"