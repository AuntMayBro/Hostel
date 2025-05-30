from django.db import models
from django.utils import timezone
from director.models import Institute , Director , Course , Branch
from hostelmanager.models import HostelManager

# Create your models here.

class Hostel(models.Model):
    name = models.CharField(max_length=100)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='hostels')
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostels')
    manager = models.ForeignKey(HostelManager, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostels')
    
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    
    contact_email = models.EmailField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    
    total_rooms = models.PositiveIntegerField(default=0)
    total_capacity = models.PositiveIntegerField(default=0)  # Total number of students that can be accommodated
    
    facilities = models.TextField(null=True, blank=True, help_text="List facilities like Wi-Fi, Mess, Laundry, Gym, etc.")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.institute.name}"

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'institute')


class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20) 
    capacity = models.PositiveIntegerField(default=1)  # Number of students the room can accommodate
    
    ROOM_TYPE_CHOICES = [
        ('S', 'Single'),
        ('D', 'Double'),
        ('T', 'Triple'),
        ('Q', 'Quad'),
    ]
    room_type = models.CharField(max_length=1, choices=ROOM_TYPE_CHOICES, default='S')
    
    # Additional info
    floor = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # If room is available
    
    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()}) - {self.hostel.name}"

    class Meta:
        unique_together = ('hostel', 'room_number')
        ordering = ['hostel', 'room_number']

class RoomAllocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='room_allocations')

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)  # Null = still allocated

    def __str__(self):
        status = "Current" if self.end_date is None else f"Ended on {self.end_date}"
        return f"{self.student.full_name()} in {self.hostel.name} Room {self.room.room_number} ({status})"

    class Meta:
        ordering = ['-start_date']
        unique_together = ('student', 'room', 'start_date')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.hostel != self.room.hostel:
            raise ValidationError("Room and Hostel mismatch.")
        if self.end_date is None:
            current_count = RoomAllocation.objects.filter(
                room=self.room, end_date__isnull=True
            ).exclude(pk=self.pk).count()
            if current_count >= self.room.capacity:
                raise ValidationError("Room is already full.")
            
