from datetime import timezone
from django.db import models
from django.utils.timezone import now
from companies.models import Companies
from roles.models import Role
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Phải cung cấp email.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Sử dụng set_password để mã hóa mật khẩu
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser phải có is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser phải có is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
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

    # role = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

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
    deleted_by = models.JSONField(default=dict, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    # 2 thuộc tính này bắt buộc khai báo để django auth xác thực 
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Sử dụng email để đăng nhập thay vì username
    REQUIRED_FIELDS = []  # Các trường khác cần khi tạo superuser

    def soft_delete(self, deleted_by=None):
    
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if deleted_by:
            self.deleted_by = deleted_by
        self.save()

    def delete(self, *args, **kwargs):
        self.soft_delete()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name
    
