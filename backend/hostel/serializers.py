from rest_framework import serializers
from django.utils import timezone
from hostel.models import ( 
    Hostel, Room, HostelManager, HostelApplication, Student, HostelImage,
    ApplicationStatus, RoomAllocation, Payment
)
from director.models import Institute, Course, Branch, Director
from account.models import User, UserRole


class HostelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelImage
        fields = ['id', 'hostel', 'image', 'caption', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']

class HostelSerializer(serializers.ModelSerializer):
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    director_info = serializers.StringRelatedField(source='director', read_only=True) 
    manager_info = serializers.StringRelatedField(source='manager.user.email', read_only=True, allow_null=True)
    hostel_type_display = serializers.CharField(source='get_hostel_type_display', read_only=True)
    occupancy_rate = serializers.FloatField(read_only=True)
    images = HostelImageSerializer(many=True, read_only=True) 

    institute = serializers.PrimaryKeyRelatedField(queryset=Institute.objects.all())
    director = serializers.PrimaryKeyRelatedField(queryset=Director.objects.all(), allow_null=True, required=False)
    manager = serializers.PrimaryKeyRelatedField(queryset=HostelManager.objects.all(), allow_null=True, required=False)


    class Meta:
        model = Hostel
        fields = [
            'id', 'name', 'institute', 'institute_name', 'director', 'director_info', 
            'manager', 'manager_info', 'images',
            'address_line1', 'address_line2', 'city', 'state', 'pincode',
            'hostel_type', 'hostel_type_display', 'total_rooms', 'available_rooms',
            'rent_per_month', 'security_deposit',
            'contact_email', 'contact_number',
            'facilities', 'wifi', 'laundry', 'mess', 'gym', 'parking', 'ac_rooms_available',
            'occupancy_rate', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'institute_name', 'director_info', 'manager_info', 'hostel_type_display',
            'occupancy_rate', 'images', 'created_at', 'updated_at'
        ]

    def validate_available_rooms(self, value):
        total_rooms_data = self.initial_data.get('total_rooms')

        if self.instance:
            total_rooms = int(total_rooms_data) if total_rooms_data is not None else self.instance.total_rooms
        else: 
            if total_rooms_data is None:
                 raise serializers.ValidationError({"total_rooms": "Total rooms is required."})
            total_rooms = int(total_rooms_data)

        if value > total_rooms:
            raise serializers.ValidationError("Available rooms cannot be greater than total rooms.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("User context is required for validation.")

        user = request.user
        is_creating = self.instance is None

        institute = data.get('institute') 
        if not institute and is_creating: 
            raise serializers.ValidationError({"institute": "Institute is required."})
        
        if institute:
            if not hasattr(user, 'director_profile') or user.director_profile.institute != institute:
                if not user.is_superuser:
                    raise serializers.ValidationError(
                        {"institute": "You can only manage hostels under your assigned institute."}
                    )
        
        if is_creating:
            if hasattr(user, 'director_profile'):
                if institute != user.director_profile.institute:
                     raise serializers.ValidationError(
                        {"institute": "Hostel institute must match your assigned institute."}
                    )
                data['director'] = user.director_profile 
            elif not user.is_superuser:
                raise serializers.ValidationError("Only a Director or Superuser can create a hostel.")
        else: # Updating
            if 'director' in data and data['director'] != self.instance.director:
                if not user.is_superuser:
                    raise serializers.ValidationError("Director cannot be changed by this user.")
            if 'institute' in data and data['institute'] != self.instance.institute:
                if not user.is_superuser: 
                     raise serializers.ValidationError("Institute cannot be changed by this user.")

        total_rooms = data.get('total_rooms', getattr(self.instance, 'total_rooms', 0))
        available_rooms = data.get('available_rooms', getattr(self.instance, 'available_rooms', 0))

        if available_rooms > total_rooms:
            raise serializers.ValidationError({
                "available_rooms": "Available rooms cannot exceed total rooms.",
                "total_rooms": "Total rooms cannot be less than available rooms."
            })
        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        manager = validated_data.get('manager')
        if manager and manager.managed_hostel and manager.managed_hostel != instance:
            raise serializers.ValidationError({'manager': "This manager is already assigned to another hostel."})
        
        return super().update(instance, validated_data)

class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    available_beds = serializers.IntegerField(read_only=True) 

    hostel = serializers.PrimaryKeyRelatedField(queryset=Hostel.objects.all())

    class Meta:
        model = Room
        fields = [
            'id', 'hostel', 'hostel_name', 'room_number', 'room_type', 'room_type_display',
            'capacity', 'current_occupancy', 'rent_per_bed', 'is_available',
            'available_beds', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'hostel_name', 'room_type_display', 'available_beds', 'created_at', 'updated_at']
       
    def validate_room_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Room number cannot be empty.")
        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be a positive integer.")
        return value

    def validate_current_occupancy(self, value):
        if value < 0:
            raise serializers.ValidationError("Current occupancy cannot be negative.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        instance = self.instance

        hostel = attrs.get('hostel', getattr(instance, 'hostel', None))
        if not hostel: 
            raise serializers.ValidationError({"hostel": "Hostel is required."})

        if user and not user.is_superuser:
            allowed = False
            if hasattr(user, 'director_profile') and hostel.director == user.director_profile:
                allowed = True
            elif hasattr(user, 'hostelmanager_profile') and hostel.manager == user.hostelmanager_profile:
                allowed = True
            
            if not allowed:
                raise serializers.ValidationError(
                    {"detail": "You do not have permission to manage rooms for this hostel."}
                )

        room_number = attrs.get('room_number', getattr(instance, 'room_number', None))
        if hostel and room_number:
            query = Room.objects.filter(hostel=hostel, room_number__iexact=room_number) 
            if instance:
                query = query.exclude(pk=instance.pk)
            if query.exists():
                raise serializers.ValidationError(
                    {"room_number": f"Room {room_number} already exists in {hostel.name}."}
                ) 

        capacity = attrs.get('capacity', getattr(instance, 'capacity', None))
        current_occupancy = attrs.get('current_occupancy', getattr(instance, 'current_occupancy', 0))

        if capacity is not None and current_occupancy > capacity:
            raise serializers.ValidationError({
                "current_occupancy": "Current occupancy cannot exceed capacity.",
                "capacity": "Capacity cannot be less than current occupancy."
            })
        
        is_available = attrs.get('is_available', getattr(instance, 'is_available', True))
        effective_capacity = capacity if capacity is not None else (instance.capacity if instance else 0)
        effective_occupancy = current_occupancy

        if is_available and effective_occupancy >= effective_capacity:
            raise serializers.ValidationError({
                "is_available": "Room cannot be marked as available if it is full or capacity is not positive."
            })
        return attrs


class HostelManagerSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    hostel_name = serializers.CharField(source='managed_hostel.name', read_only=True, allow_null=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=UserRole.MANAGER))
    institute = serializers.PrimaryKeyRelatedField(queryset=Institute.objects.all())

    class Meta:
        model = HostelManager
        fields = [
            'id', 'user', 'user_email', 'institute', 'institute_name', 'hostel_name',
            'designation', 'contact_number', 'alternate_contact_number',
            'address', 'city', 'state', 'pincode', 'profile_picture',
            'start_date', 'end_date', 'is_currently_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'institute_name', 'hostel_name', 
                            'is_currently_active', 'created_at', 'updated_at']

    def validate_user(self, value):
        if value.role != UserRole.MANAGER:
            raise serializers.ValidationError("User must have the 'Manager' role.")

        if HostelManager.objects.filter(user=value, end_date__isnull=True).exists() and (not self.instance or self.instance.user != value) :
            raise serializers.ValidationError("This user is already an active hostel manager.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        acting_user = request.user if request else None
        
        institute = attrs.get('institute')

        if acting_user and not acting_user.is_superuser:
            if not hasattr(acting_user, 'director_profile'):
                raise serializers.ValidationError("You must be a Director to manage Hostel Managers.")
            if institute and acting_user.director_profile.institute != institute:
                raise serializers.ValidationError("You can only assign managers within your own institute.")
        return attrs
    
class StudentProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True, allow_null=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True, allow_null=True)
    full_name = serializers.CharField(read_only=True) 

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'user_email', 'full_name', 'institute', 'institute_name', 
            'course', 'course_name', 'branch', 'branch_name', 'enroll_number', 'registration_number',
            'date_of_birth', 'gender', 'phone_number', 'year_of_study', 'admission_year',
            'admission_date', 'leaving_date', 'is_active_student', 'is_currently_hosteller',
            'emergency_contact_name', 'emergency_contact_phone',
            'address_line1', 'address_line2', 'city', 'state', 'pincode',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'user_email', 'full_name', 'institute_name', 'course_name', 'branch_name',
                            'is_currently_hosteller', 'created_at', 'updated_at')

class HostelApplicationSerializer(serializers.ModelSerializer):
    student_info = StudentProfileSerializer(source='student', read_only=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    preferred_hostel_name = serializers.CharField(source='preferred_hostel.name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True, allow_null=True)

    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=False)
    institute = serializers.PrimaryKeyRelatedField(queryset=Institute.objects.all())
    preferred_hostel = serializers.PrimaryKeyRelatedField(queryset=Hostel.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = HostelApplication
        fields = [
            'id', 'student', 'student_info', 'institute', 'institute_name', 
            'course_at_application', 'branch_at_application',
            'preferred_hostel', 'preferred_hostel_name', 'preferred_room_type', 
            'reason_for_hostel', 'status', 'status_display', 
            'reviewed_by', 'reviewed_by_email', 'remarks_by_reviewer',
            'submitted_at', 'reviewed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_info', 'institute_name', 'preferred_hostel_name', 
            'status_display', 'reviewed_by', 'reviewed_by_email', 
            'submitted_at', 'reviewed_at', 'created_at', 'updated_at'
        ]

    def validate_student(self, value):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            if value != request.user.student_profile:
                raise serializers.ValidationError("You can only submit an application for yourself.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        
        is_creating = self.instance is None

        if is_creating:
            if not user or not hasattr(user, 'student_profile'):
                raise serializers.ValidationError("Only authenticated students can submit hostel applications.")
            
            student_profile = user.student_profile
            data['student'] = student_profile

            if HostelApplication.objects.filter(
                student=student_profile,
                status__in=[ApplicationStatus.PENDING, ApplicationStatus.APPROVED, ApplicationStatus.WAITLISTED]
            ).exists():
                raise serializers.ValidationError("You already have an active or approved hostel application.")
            
            if data.get('institute') != student_profile.institute:
                raise serializers.ValidationError("Application institute must match your registered institute.")
            
            data['course_at_application'] = student_profile.course
            data['branch_at_application'] = student_profile.branch

        if not is_creating and 'status' in data and data['status'] != self.instance.status:
            if not user or not (user.is_superuser or hasattr(user, 'director_profile') or hasattr(user, 'hostelmanager_profile')):
                raise serializers.ValidationError({"status": "You do not have permission to change the application status."})
            
            data['reviewed_by'] = user
            data['reviewed_at'] = timezone.now()

            if data['status'] == ApplicationStatus.APPROVED:
                pass

        preferred_hostel = data.get('preferred_hostel')
        application_institute = data.get('institute', getattr(self.instance, 'institute', None))
        if preferred_hostel and application_institute and preferred_hostel.institute != application_institute:
            raise serializers.ValidationError({
                "preferred_hostel": "Preferred hostel does not belong to the selected institute."
            })
            
        return data

    def create(self, validated_data):
        validated_data['status'] = ApplicationStatus.PENDING
        validated_data['submitted_at'] = timezone.now()
        return super().create(validated_data)
    
class RoomAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    hostel_name = serializers.CharField(source='room.hostel.name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    application = serializers.PrimaryKeyRelatedField(queryset=HostelApplication.objects.filter(status=ApplicationStatus.APPROVED), required=False, allow_null=True)


    class Meta:
        model = RoomAllocation
        fields = [
            'id', 'student', 'student_name', 'room', 'room_number', 'hostel_name', 
            'application', 'start_date', 'end_date', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'student_name', 'room_number', 'hostel_name', 'is_active', 
            'created_at', 'updated_at'
        )

    def validate(self, attrs):
        instance = self.instance
        is_creating = instance is None

        student = attrs.get('student', getattr(instance, 'student', None))
        room = attrs.get('room', getattr(instance, 'room', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', timezone.now().date()))
        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))

        if end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date."})

        is_currently_active_allocation = (end_date is None or end_date >= timezone.now().date())

        if is_currently_active_allocation and room:
            query = RoomAllocation.objects.filter(room=room, end_date__isnull=True)
            if instance:
                query = query.exclude(pk=instance.pk)
            
            active_occupants = query.count()
            
            if active_occupants >= room.capacity:

                if not (instance and instance.student == student and instance.room == room and instance.is_active):
                    raise serializers.ValidationError(
                        {"room": f"Room {room.room_number} is already at full capacity ({room.capacity} occupants)."}
                    )

        if is_currently_active_allocation and student:
            query = RoomAllocation.objects.filter(student=student, end_date__isnull=True)
            if instance: 
                query = query.exclude(pk=instance.pk)
            if query.exists():
                 raise serializers.ValidationError(
                    {"student": f"Student {student} is already actively allocated to another room."}
                )
        application = attrs.get('application')
        if application:
            if application.status != ApplicationStatus.APPROVED:
                raise serializers.ValidationError({"application": "Hostel application is not approved."})
            if application.student != student:
                raise serializers.ValidationError({"application": "Application does not belong to the selected student."})
            if application.allocation and (not instance or application.allocation.pk != instance.pk):
                raise serializers.ValidationError({"application": "This application is already linked to another allocation."})

        return attrs

class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    room_allocation_info = serializers.StringRelatedField(source='room_allocation', read_only=True, allow_null=True)

    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    room_allocation = serializers.PrimaryKeyRelatedField(queryset=RoomAllocation.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'student_name', 'room_allocation', 'room_allocation_info',
            'payment_type', 'payment_type_display', 'amount', 'status', 'status_display',
            'due_date', 'payment_date', 'transaction_id', 'payment_method', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'student_name', 'payment_type_display', 'status_display', 
            'room_allocation_info', 'created_at', 'updated_at'
        )

    def validate(self, attrs):
        student = attrs.get('student')
        room_allocation = attrs.get('room_allocation')
        if room_allocation and student and room_allocation.student != student:
            raise serializers.ValidationError(
                {"room_allocation": "Room allocation does not belong to the selected student."}
            )
        return attrs
