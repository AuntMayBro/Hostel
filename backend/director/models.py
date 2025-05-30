from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Institute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    contact_email = models.EmailField(null=True, blank=True)
    contact_number = PhoneNumberField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    
    class Meta:
        unique_together = ('code', 'course')

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.institute.name}"
    
class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='branches')

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.course.name} - {self.course.institute.name}"
    
class Director(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='directors')

    designation = models.CharField(max_length=100, default="Director")
    contact_number = PhoneNumberField(null=True, blank=True)
    alternate_contact_number = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(help_text="Use '\\n' for line breaks, e.g., Line1\\nLine2\\nLine3")

    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    profile_picture = models.ImageField(upload_to='director_profiles/', null=True, blank=True)

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.institute.name})"

    @property
    def is_active(self):
        return self.end_date is None

    def formatted_address(self):
        """Splits address into lines for display"""
        return self.address.split('\n')