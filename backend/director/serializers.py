from rest_framework import serializers
from director.models import Institute, Course, Branch, Director
from account.models import User, UserRole 
from django.contrib.auth.password_validation import validate_password
from django.db import transaction 

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class DirectorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    institute_name = serializers.CharField(write_only=True, source='institute.name', required=True)
    institute_address = serializers.CharField(write_only=True, source='institute.address', required=True)
    institute_city = serializers.CharField(write_only=True, source='institute.city', required=True)
    institute_state = serializers.CharField(write_only=True, source='institute.state', required=True)
    institute_pincode = serializers.CharField(write_only=True, source='institute.pincode', required=True)

    class Meta:
        model = Director
        fields = (
            'id', 'email', 'password',
            'first_name', 'last_name',
            'institute_name', 'institute_address', 'institute_city', 'institute_state', 'institute_pincode',
            # Director fields from model
            'designation', 'contact_number', 'alternate_contact_number',
            'address', 'city', 'state', 'pincode', 'profile_picture',
            'institute', 
            'user'
        )
        read_only_fields = ('id', 'institute', 'user')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_institute_name(self, value): # Validating the institute name specifically
        if Institute.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("An institute with this name already exists.")
        return value

    @transaction.atomic 
    def create(self, validated_data):
        institute_data = {
            'name': validated_data.pop('institute.name'),
            'address': validated_data.pop('institute.address'),
            'city': validated_data.pop('institute.city'),
            'state': validated_data.pop('institute.state'),
            'pincode': validated_data.pop('institute.pincode'),
        }
        institute, created = Institute.objects.get_or_create(name=institute_data['name'], defaults=institute_data)
        if not created and any(institute_data[key] != getattr(institute, key) for key in institute_data if hasattr(institute, key)):
             pass

        user_email = validated_data.pop('email')
        user_password = validated_data.pop('password')
        
        user = User.objects.create_user(
            email=user_email,
            password=user_password,
            role=UserRole.DIRECTOR,
            is_active=True
        )

        director_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'designation': validated_data.get('designation', "Director"),
            'contact_number': validated_data.get('contact_number'),
            'alternate_contact_number': validated_data.get('alternate_contact_number'),
            'address': validated_data.get('address'),
            'city': validated_data.get('city'),
            'state': validated_data.get('state'),
            'pincode': validated_data.get('pincode'),
            'profile_picture': validated_data.get('profile_picture'),
        }
        
        director = Director.objects.create(
            user=user,
            institute=institute,
            **director_data
        )
        return director

# Course and Branch Serializer
class BranchSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'code', 'course', 'course_name', 'created_at', 'updated_at']
        read_only_fields = ('id', 'course_name', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'query_params'): 
            institute_id = request.query_params.get('institute_id')
            if institute_id:
                try:
                    institute = Institute.objects.get(pk=institute_id)
                    self.fields['course'].queryset = Course.objects.filter(institute=institute)
                except Institute.DoesNotExist:
                    self.fields['course'].queryset = Course.objects.none()
                except ValueError: 
                    self.fields['course'].queryset = Course.objects.none()

    def validate(self, attrs):
        course = attrs.get('course')
        request = self.context.get('request')

        if request and hasattr(request, 'query_params'):
            institute_id_param = request.query_params.get('institute_id')
            if institute_id_param and course:
                try:
                    if course.institute_id != int(institute_id_param):
                        raise serializers.ValidationError(
                            {"course": f"This course does not belong to the specified institute (ID: {institute_id_param})."}
                        )
                except ValueError:
                     raise serializers.ValidationError({"course": "Invalid institute ID in query parameter."})
        return attrs

class CourseSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'name', 'code', 'institute', 'institute_name', 'branches',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'institute_name', 'branches', 'created_at', 'updated_at')

    def validate(self, attrs):
        if not attrs.get('institute') and not self.instance:
            raise serializers.ValidationError({"institute": "Institute is required for creating a course."})
        return attrs