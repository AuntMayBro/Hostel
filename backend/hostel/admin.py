from django.contrib import admin
from .models import (
    Hostel, 
    Room, 
    HostelManager, 
    HostelApplication, 
    Student, 
    HostelImage,
    RoomAllocation, 
    Payment
)

#Register your models here.
admin.site.register(Hostel)
admin.site.register(Room)
admin.site.register(HostelManager)
admin.site.register(HostelApplication)
admin.site.register(Student)
admin.site.register(HostelImage)
admin.site.register(RoomAllocation)
admin.site.register(Payment)

