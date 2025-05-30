from django.db import models
from django.conf import settings
from director.models import Institute , Director , Course , Branch
from hostel.models import Room ,RoomAllocation , Hostel

# Create your models here.

class HostelManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='hostel_managers')
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_managers')
    hostel = models.OneToOneField(Hostel, on_delete=models.CASCADE, related_name='manager')

    designation = models.CharField(max_length=100, default="Hostel Manager")
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    alternate_contact_number = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(help_text="Use '\\n' for line breaks, e.g., Line1\\nLine2\\nLine3")
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    profile_picture = models.ImageField(upload_to='hostel_manager_profiles/', null=True, blank=True)

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hostel.name}"

    @property
    def is_active(self):
        return self.end_date is None

    def formatted_address(self):
        return self.address.split('\n')