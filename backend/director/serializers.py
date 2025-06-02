from rest_framework import serializers
from .models import *
from account.models import User, UserRole

# serializers 

class InstituteSerializer(serializers.ModelSerializer):
    class Meta :
        model = Institute
        fields = '__all__'

class DirectorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    institute = InstituteSerializer()

    class Meta:
        model = Director
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
            'designation',
            'contact_number',
            'alternate_contact_number',
            'address',
            'city',
            'state',
            'pincode',
            'profile_picture',
            'institute', 
        )

    def validate_institute(self, institute_data):
        name = institute_data.get('name')
        if Institute.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError("An institute with this name already exists.")
        return institute_data

    def create(self, validated_data):
        institute_data = validated_data.pop('institute')
        institute = Institute.objects.create(**institute_data)

        user = User.objects.create_user(
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            role=UserRole.DIRECTOR,
            is_active=True
        )

        director = Director.objects.create(
            user=user,
            institute=institute,
            **validated_data
        )
        return director
    

# Course and Branch Serializer

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'code', 'course']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request:
            institute_id = request.query_params.get('institute_id')
            if institute_id:
                self.fields['course'].queryset = Course.objects.filter(institute_id=institute_id)
            else:
                self.fields['course'].queryset = Course.objects.none()

class CourseSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = (
            'name',
            'code',
            'institute',
            'branches',
        )