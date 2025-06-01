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
        exclude = ['user', 'start_date', 'end_date']

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
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            role=UserRole.DIRECTOR,
            is_active=True
        )

        director = Director.objects.create(
            user=user,
            institute=institute,
            **validated_data
        )
        return director