from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.core.exceptions import ValidationError
from director.models import Institute, Course, Branch, Director



class Hostel(models.Model):
    HOSTEL_TYPES = (
        ('boys', 'Boys Hostel'),
        ('girls', 'Girls Hostel'),
        ('mixed', 'Mixed Hostel'),
    )

    name = models.CharField(max_length=100)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='hostels')
    director = models.ForeignKey(
        Director, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='directed_hostels'
    )
    manager = models.OneToOneField(
        'HostelManager', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='managed_hostel'
    )
    
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10) 

    hostel_type = models.CharField(max_length=10, choices=HOSTEL_TYPES)
    total_rooms = models.PositiveIntegerField(default=0) 
    available_rooms = models.PositiveIntegerField(default=0)
    rent_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)

    contact_email = models.EmailField(null=True, blank=True)
    contact_number = PhoneNumberField(null=True, blank=True)

    facilities = models.TextField(null=True, blank=True, help_text="List facilities like Wi-Fi, Mess, Laundry, Gym, etc., separated by commas.")
    wifi = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    mess = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    ac_rooms_available = models.BooleanField(default=False, verbose_name="AC Rooms Available") 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'institute')
        verbose_name = "Hostel"
        verbose_name_plural = "Hostels"

    def __str__(self):
        return f"{self.name} - {self.institute.name}"

    @property
    def occupancy_rate(self):
        if self.total_rooms == 0:
            return 0.0
        occupied_rooms = self.total_rooms - self.available_rooms
        occupied_rooms = max(0, occupied_rooms) 
        return round((occupied_rooms / self.total_rooms) * 100, 2) if self.total_rooms > 0 else 0.0
    
    def clean(self):
        super().clean()
        if self.available_rooms > self.total_rooms:
            raise ValidationError({'available_rooms': 'Available rooms cannot exceed total rooms.'})

class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hostel_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False) # Consider logic to ensure only one primary image per hostel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.hostel.name}" + (" (Primary)" if self.is_primary else "")

    class Meta:
        ordering = ['-is_primary', '-created_at']
        verbose_name = "Hostel Image"
        verbose_name_plural = "Hostel Images"

class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Single Occupancy'),
        ('double', 'Double Occupancy'),
        ('triple', 'Triple Occupancy'),
        ('dormitory', 'Dormitory (Multiple Occupancy)'),
    )
  
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    rent_per_bed = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hostel', 'room_number')
        ordering = ['hostel', 'room_number']
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    @property
    def available_beds(self):
        return max(0, self.capacity - self.current_occupancy)

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()}) - {self.hostel.name}"

    def clean(self):
        super().clean()
        if self.current_occupancy > self.capacity:
            raise ValidationError({'current_occupancy': 'Current occupancy cannot exceed room capacity.'})
        if self.is_available and self.available_beds <= 0:
            raise ValidationError({'is_available': 'A full room cannot be marked as available.'})


class HostelManager(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='hostelmanager'
    )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='hostel_managers_profiles')

    designation = models.CharField(max_length=100, default="Hostel Manager")
    contact_number = PhoneNumberField(null=True, blank=True)
    alternate_contact_number = PhoneNumberField(null=True, blank=True) # Changed to PhoneNumberField

    address = models.TextField(help_text="Full address", blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    profile_picture = models.ImageField(upload_to='hostel_manager_profiles/', null=True, blank=True)

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_currently_active(self): 
        return self.end_date is None and self.user.is_active

    def __str__(self):
        user_name = self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.email
        try:
            hostel_name = self.managed_hostel.name 
        except Hostel.DoesNotExist: 
             hostel_name = "No hostel assigned"
        except AttributeError: 
            hostel_name = "Hostel not linked"

        return f"{user_name} (Manager for {hostel_name})"

    class Meta:
        ordering = ['user__email']
        verbose_name = "Hostel Manager"
        verbose_name_plural = "Hostel Managers"

class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='student'
    )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='students_profiles')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    enroll_number = models.CharField(max_length=30, unique=True)
    registration_number = models.CharField(max_length=30, unique=True, null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    phone_number = PhoneNumberField(null=True, blank=True) 

    year_of_study = models.PositiveSmallIntegerField(null=True, blank=True)
    admission_year = models.PositiveSmallIntegerField(null=True, blank=True)

    admission_date = models.DateField(null=True, blank=True)
    leaving_date = models.DateField(null=True, blank=True)

    is_currently_hosteller = models.BooleanField(default=False) 
    is_active_student = models.BooleanField(default=True, verbose_name="Is Active Student in Institute")

    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = PhoneNumberField(null=True, blank=True)

    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_name = self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.email
        return f"{user_name} ({self.enroll_number})"

    @property
    def full_name(self):
        return self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.email
    
    @property
    def is_currently_hosteller(self):
        """Checks if the student has an active room allocation."""
        return self.room_allocations.filter(end_date__isnull=True).exists()

    class Meta:
        ordering = ['institute', 'enroll_number']
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

class ApplicationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled by Student'
    WAITLISTED = 'waitlisted', 'Waitlisted'

class HostelApplication(models.Model):
    PREFERRED_ROOM_TYPES = [
        ('single', 'Single Occupancy'),
        ('double', 'Double Occupancy'),
        ('triple', 'Triple Occupancy'),
        ('any', 'Any Available')
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_applications')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)

    course_at_application = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    branch_at_application = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    preferred_hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_room_type = models.CharField(max_length=20, choices=PREFERRED_ROOM_TYPES, default='any')

    reason_for_hostel = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='reviewed_hostel_applications'
    )
    remarks_by_reviewer = models.TextField(null=True, blank=True)

    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application by {self.student} - Status: {self.get_status_display()}"

    def clean(self):
        super().clean()
        if self.student and self.institute != self.student.institute:
            raise ValidationError("Application institute must match student's institute.")

        if self.status in [ApplicationStatus.PENDING, ApplicationStatus.APPROVED, ApplicationStatus.WAITLISTED]:
            existing_active_apps = HostelApplication.objects.filter(
                student=self.student,
                status__in=[ApplicationStatus.PENDING, ApplicationStatus.APPROVED, ApplicationStatus.WAITLISTED]
            ).exclude(pk=self.pk)
            if existing_active_apps.exists():
                raise ValidationError(f"Student {self.student} already has an active or approved hostel application.")
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Hostel Application"
        verbose_name_plural = "Hostel Applications"


class RoomAllocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='all_room_allocations')
    application = models.OneToOneField(HostelApplication, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocation')

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'student']
        unique_together = ('student', 'room', 'start_date')

    def __str__(self):
        status = "Current" if self.is_active else f"Ended on {self.end_date.strftime('%Y-%m-%d') if self.end_date else 'N/A'}"
        return f"{self.student} in Room {self.room.room_number} ({self.room.hostel.name}) - {status}"

    @property
    def hostel(self):
        return self.room.hostel

    @property
    def is_active(self):
        return self.end_date is None or self.end_date >= timezone.now().date()

    def clean(self):
        super().clean()
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date.")

        if self.is_active: 
            active_allocations_for_room = RoomAllocation.objects.filter(
                room=self.room, end_date__isnull=True
            ).exclude(pk=self.pk if self.pk else None).count()
            
            effective_occupancy = active_allocations_for_room + (1 if not self.pk or RoomAllocation.objects.get(pk=self.pk).end_date is not None else 0)

            if effective_occupancy >= self.room.capacity:
                if not (self.pk and RoomAllocation.objects.get(pk=self.pk).end_date is None and active_allocations_for_room < self.room.capacity):
                    raise ValidationError(f"Room {self.room.room_number} is already at full capacity ({self.room.capacity} occupants).")

        other_active_allocations_for_student = RoomAllocation.objects.filter(
            student=self.student, end_date__isnull=True
        ).exclude(pk=self.pk if self.pk else None)
        if self.is_active and other_active_allocations_for_student.exists():
            raise ValidationError(f"Student {self.student} is already actively allocated to another room.")

class Payment(models.Model):
    PAYMENT_TYPES = (
        ('security_deposit', 'Security Deposit'),
        ('rent', 'Rent'),
        ('maintenance_fee', 'Maintenance Fee'),
        ('other', 'Other Fee'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('waived', 'Waived'),
    )
    
    room_allocation = models.ForeignKey(RoomAllocation, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')

    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)

    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.student}: {self.amount} ({self.get_payment_type_display()}) - Status: {self.get_status_display()}"

    class Meta:
        ordering = ['-due_date', 'student']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
