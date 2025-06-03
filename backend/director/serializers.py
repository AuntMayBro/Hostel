from rest_framework import serializers
from director.models import Institute, Course, Branch, Director
from account.models import User, UserRole 
from django.contrib.auth.password_validation import validate_password
from django.db import transaction 
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class InstituteSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    pincode = serializers.CharField(required=True)
    contact_email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    contact_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    website = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Institute
        fields = (
            'name', 'address', 'city', 'state', 'pincode',
            'contact_email', 'contact_number', 'website'
        )
        read_only_fields = ('created_at', 'updated_at') # Assuming these fields exist on Institute model

class DirectorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    institute = InstituteSerializer(write_only=True, required=True)

    class Meta:
        model = Director
        fields = (
            # User fields
            'id', 'email', 'password',

            # Director model fields
            'first_name', 'last_name', 'designation', 'contact_number',
            'alternate_contact_number', 'address', 'city', 'state', 'pincode',
            'profile_picture',

            # Institute (nested or ID)
            'institute',
        )
        read_only_fields = ('id', 'user')

    def validate(self, data):
        super().validate(data)

        institute_data = data.get('institute')
        if institute_data and 'name' in institute_data:
            institute_name = institute_data['name']
            if Institute.objects.filter(name__iexact=institute_name).exists():
                raise serializers.ValidationError({"institute": {"name": "An institute with this name already exists."}})
        return data

    @transaction.atomic 
    def create(self, validated_data):
        institute_data = validated_data.pop('institute')
        user_email = validated_data.pop('email')
        user_password = validated_data.pop('password')

        institute, created = Institute.objects.get_or_create(
            name=institute_data['name'], 
            defaults=institute_data
        )
        
        if not created:
            for key, value in institute_data.items():
                setattr(institute, key, value)
            institute.save()

       
        User = get_user_model()
        try:
            user = User.objects.get(email=user_email)
            if not user.check_password(user_password):
                raise ValidationError("Password is incorrect.")
        except User.DoesNotExist:
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