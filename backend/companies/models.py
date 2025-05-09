from django.db import models
from datetime import datetime, timezone

# Create your models here.

class Companies(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    deletedAt = models.DateTimeField(blank=True, null=True)
    createdBy = models.JSONField(blank=True, null=True)
    updatedBy = models.JSONField(blank=True, null=True)
    deletedBy = models.JSONField(blank=True, null=True)

    def soft_delete(self, deleted_by=None):
    
        now = datetime.now(timezone.utc)  # lấy thời gian UTC hiện tại
        self.isDeleted = True
        self.deletedAt = now
        if deleted_by:
            self.deletedBy = deleted_by
        self.save()
        return self

    class Meta:  
        db_table = "companies"