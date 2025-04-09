from django.db import models

# Create your models here.

class Companies(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    deletedAt = models.DateTimeField(blank=True, null=True)
    createdBy = models.JSONField(blank=True, null=True)
    updated_by = models.JSONField(blank=True, null=True)
    delete_by = models.JSONField(blank=True, null=True)


    class Meta:  
        db_table = "companies"