from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

class UserRole(models.TextChoices):
    DIRECTOR = 'director', 'Director'
    MANAGER = 'manager', 'Manager'
    STUDENT = 'student', 'Student'
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)

        role = extra_fields.get('role')
        if role and role not in UserRole.values:
            raise ValueError(f"Invalid role: {role}")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True) 
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.DIRECTOR)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin): 
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )

    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.STUDENT, 
        verbose_name="User Role"
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False) 
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] 

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def is_student_role(self):
        return self.role == UserRole.STUDENT
    
    @property
    def is_manager_role(self):
        return self.role == UserRole.MANAGER
    
    @property
    def is_director_role(self):
        return self.role == UserRole.DIRECTOR

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
