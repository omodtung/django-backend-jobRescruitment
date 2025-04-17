
from django.utils import timezone
from django.db import models
from permissions.models   import Permissions

class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)  # Added unique constraint
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permissions,  # Changed to Django's default Permission model
        related_name='roles',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Using callable defaults for JSONFields to avoid mutable default issues
    created_by = models.JSONField(
        blank=True, null=True,
        help_text="Object containing creator details, e.g., {'_id': ObjectID, 'email': string}"
    )
    updated_by = models.JSONField(
        blank=True, null=True,
        help_text="Object containing updater details, e.g., {'_id': ObjectID, 'email': string}"
    )
    deleted_by = models.JSONField(default=dict, blank=True)  # Corrected field name
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "roles"  # Recommended lowercase naming convention
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']  # Default ordering
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_deleted']),
        ]

    def soft_delete(self, deleted_by=None):
    
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if deleted_by:
            self.deleted_by = deleted_by
        self.save()
        return self