from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from director.models import Institute , Director , Course , Branch
from hostel.models import Room ,RoomAllocation , Hostel

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    
    Enroll_number = models.CharField(max_length=30, unique=True)
    registration_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    
    # Personal info
    date_of_birth = models.DateField(null=True, blank=True)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices, null=True, blank=True)
    
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    # Academic info
    year_of_study = models.PositiveSmallIntegerField(null=True, blank=True)
    admission_year = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Hostel info
    hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    
    # Status and dates
    admission_date = models.DateField(null=True, blank=True)
    leaving_date = models.DateField(null=True, blank=True)
    
    is_currently_hosteller = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Additional fields
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = PhoneNumberField(null=True, blank=True)

    
    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"

    class Meta:
        ordering = ['Enroll_number']