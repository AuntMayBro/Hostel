from django.contrib import admin
from .models import Director, Course, Branch, Institute
# Register your models here.

admin.site.register(Director)
admin.site.register(Course)
admin.site.register(Branch)
admin.site.register(Institute)