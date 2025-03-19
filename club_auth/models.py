from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, studentId, password=None, **extra_fields):
        if not studentId:
            raise ValueError("The Student ID is required")
        extra_fields.setdefault("is_active", True)
        user = self.model(studentId=studentId, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, studentId, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(studentId, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # Remove username
    studentId = models.IntegerField(unique=True)  # Use studentId instead
    name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default="avatars/avatar.jpeg")

    objects = CustomUserManager()  # Use the new manager

    USERNAME_FIELD = 'studentId'  # Login with studentId instead of username
    REQUIRED_FIELDS = ['email']  # Required for superuser creation

    def __str__(self):
        return f"{self.studentId} - {self.name}"
