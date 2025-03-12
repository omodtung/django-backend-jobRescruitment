from django.db import models
from django.utils.timezone import now
from companies.models import Companies

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Setting up a ForeignKey relationship with the Company model
    company = models.ForeignKey(
       Companies,  # Referencing the Company model
        on_delete=models.SET_NULL,  # Set the `company` field to NULL if the referenced Company is deleted
        null=True,
        blank=True,
        related_name='users',  # Enables a reverse lookup from `Company` to `User`
        help_text="Reference to the associated company."
    )

    role = models.CharField(max_length=255, blank=True, null=True)

    refresh_token = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.JSONField(
        blank=True, null=True,
        help_text="Object containing creator details, e.g., {'_id': ObjectID, 'email': string}"
    )
    updated_by = models.JSONField(
        blank=True, null=True,
        help_text="Object containing updater details, e.g., {'_id': ObjectID, 'email': string}"
    )

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name