
# Create your models here.
from django.db import models
from datetime import datetime, timezone


class Permissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    api_path = models.CharField(max_length=255)
    method = models.CharField(max_length=50)
    module = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.JSONField(default=dict, blank=True)
    updated_by = models.JSONField(default=dict, blank=True)
    delete_by = models.JSONField(default=dict, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self, deleted_by=None):
    
        now = datetime.now(timezone.utc)  # lấy thời gian UTC hiện tại
        self.is_deleted = True
        self.deleted_at = now
        if deleted_by:
            self.deleted_by = deleted_by
        self.save()
        return self


    def __str__(self):
        return self.name
    
        
    class Meta:
        db_table = "Permissions"