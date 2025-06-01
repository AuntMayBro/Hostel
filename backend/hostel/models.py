from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore
from django.conf import settings
from director.models import Institute, Course, Branch, Director


class Hostel(models.Model):
    """Represents a hostel within an institute."""
    name = models.CharField(max_length=100)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='hostels')
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostels')
    manager = models.OneToOneField('HostelManager', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_hostel')
    

    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    contact_email = models.EmailField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)

    total_rooms = models.PositiveIntegerField(default=0)
    total_capacity = models.PositiveIntegerField(default=0)

    facilities = models.TextField(null=True, blank=True, help_text="List facilities like Wi-Fi, Mess, Laundry, Gym, etc.")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'institute')

    def __str__(self):
        return f"{self.name} - {self.institute.name}"


class Room(models.Model):
    """Represents a room within a hostel."""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=1)

    ROOM_TYPE_CHOICES = [
        ('S', 'Single'),
        ('D', 'Double'),
        ('T', 'Triple'),
        ('Q', 'Quad'),
    ]
    room_type = models.CharField(max_length=1, choices=ROOM_TYPE_CHOICES, default='S')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['hostel', 'room_number']
        unique_together = ('hostel', 'room_number')

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()}) - {self.hostel.name}"


class HostelManager(models.Model):
    """Manages hostel operations."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='hostel_managers')
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_managers')
    hostel = models.OneToOneField(Hostel, on_delete=models.CASCADE, related_name='hostel_manager')

    designation = models.CharField(max_length=100, default="Hostel Manager")
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    alternate_contact_number = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(help_text="Use '\\n' for line breaks.")
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    profile_picture = models.ImageField(upload_to='hostel_manager_profiles/', null=True, blank=True)

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        return self.end_date is None

    def formatted_address(self):
        return self.address.split('\n')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hostel.name}"


class ApplicationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled'

class HostelApplication(models.Model):
    """Captures hostel accommodation requests from students."""
    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='hostel_application')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    preferred_hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_room_type = models.CharField(max_length=20, choices=[
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('any', 'Any Available')
    ], default='any')

    reason_for_hostel = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_applications')

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.status}"


class RoomAllocation(models.Model):
    """Represents the allocation of a student to a room."""
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='room_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='room_allocations')

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ('student', 'room', 'start_date')

    def __str__(self):
        status = "Current" if not self.end_date else f"Ended on {self.end_date}"
        return f"{self.student.full_name()} in {self.hostel.name} Room {self.room.room_number} ({status})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.hostel != self.room.hostel:
            raise ValidationError("Room and Hostel mismatch.")
        if self.end_date is None:
            current_count = RoomAllocation.objects.filter(room=self.room, end_date__isnull=True).exclude(pk=self.pk).count()
            if current_count >= self.room.capacity:
                raise ValidationError("Room is already full.")



#Students Models
class Student(models.Model):
    """Represents a student who may apply for and reside in a hostel."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    enroll_number = models.CharField(max_length=30, unique=True)
    registration_number = models.CharField(max_length=30, unique=True, null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)

    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    year_of_study = models.PositiveSmallIntegerField(null=True, blank=True)
    admission_year = models.PositiveSmallIntegerField(null=True, blank=True)

    hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    admission_date = models.DateField(null=True, blank=True)
    leaving_date = models.DateField(null=True, blank=True)

    is_currently_hosteller = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = PhoneNumberField(null=True, blank=True)

    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.enroll_number})"

    def full_name(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['enroll_number']
