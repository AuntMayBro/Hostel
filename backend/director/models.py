from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField # type: ignore

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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Institute"
        verbose_name_plural = "Institutes"
    
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20) # Increased length slightly
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='courses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
         unique_together = ('code', 'institute')
         ordering = ['institute', 'name']
         verbose_name = "Course"
         verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.institute.name}"
    
class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='branches')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
         unique_together = ('code', 'course')
         ordering = ['course', 'name']
         verbose_name = "Branch"
         verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.course.name}"
    
class Director(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='director'
    )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='directors')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100) 

    designation = models.CharField(max_length=100, default="Director")
    contact_number = PhoneNumberField(null=True, blank=True)
    alternate_contact_number = PhoneNumberField(null=True, blank=True)

    address = models.TextField(help_text="Full address", blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    profile_picture = models.ImageField(upload_to='director_profiles/', null=True, blank=True)

    start_date = models.DateField(auto_now_add=True) 
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_name = self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user.email
        return f"{user_name} ({self.institute.name})"

    @property
    def is_currently_active(self): 
        return self.end_date is None and self.user.is_active

    class Meta:
        ordering = ['institute', 'user__email'] 
        verbose_name = "Director"
        verbose_name_plural = "Directors"