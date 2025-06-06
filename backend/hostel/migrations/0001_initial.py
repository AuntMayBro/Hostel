# Generated by Django 5.2.1 on 2025-06-03 11:26

import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('director', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hostel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address_line1', models.CharField(max_length=200)),
                ('address_line2', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=10)),
                ('hostel_type', models.CharField(choices=[('boys', 'Boys Hostel'), ('girls', 'Girls Hostel'), ('mixed', 'Mixed Hostel')], max_length=10)),
                ('total_rooms', models.PositiveIntegerField(default=0)),
                ('available_rooms', models.PositiveIntegerField(default=0)),
                ('rent_per_month', models.DecimalField(decimal_places=2, max_digits=10)),
                ('security_deposit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('contact_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('facilities', models.TextField(blank=True, help_text='List facilities like Wi-Fi, Mess, Laundry, Gym, etc., separated by commas.', null=True)),
                ('wifi', models.BooleanField(default=False)),
                ('laundry', models.BooleanField(default=False)),
                ('mess', models.BooleanField(default=False)),
                ('gym', models.BooleanField(default=False)),
                ('parking', models.BooleanField(default=False)),
                ('ac_rooms_available', models.BooleanField(default=False, verbose_name='AC Rooms Available')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('director', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='directed_hostels', to='director.director')),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hostels', to='director.institute')),
            ],
            options={
                'verbose_name': 'Hostel',
                'verbose_name_plural': 'Hostels',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HostelApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_room_type', models.CharField(choices=[('single', 'Single Occupancy'), ('double', 'Double Occupancy'), ('triple', 'Triple Occupancy'), ('any', 'Any Available')], default='any', max_length=20)),
                ('reason_for_hostel', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled by Student'), ('waitlisted', 'Waitlisted')], default='pending', max_length=20)),
                ('remarks_by_reviewer', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch_at_application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='director.branch')),
                ('course_at_application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='director.course')),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='director.institute')),
                ('preferred_hostel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hostel.hostel')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_hostel_applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Hostel Application',
                'verbose_name_plural': 'Hostel Applications',
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.CreateModel(
            name='HostelImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='hostel_images/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('is_primary', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='hostel.hostel')),
            ],
            options={
                'verbose_name': 'Hostel Image',
                'verbose_name_plural': 'Hostel Images',
                'ordering': ['-is_primary', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HostelManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(default='Hostel Manager', max_length=100)),
                ('contact_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('alternate_contact_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('address', models.TextField(blank=True, help_text='Full address')),
                ('city', models.CharField(blank=True, max_length=50)),
                ('state', models.CharField(blank=True, max_length=50)),
                ('pincode', models.CharField(blank=True, max_length=10)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='hostel_manager_profiles/')),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hostel_managers_profiles', to='director.institute')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hostelmanager', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Hostel Manager',
                'verbose_name_plural': 'Hostel Managers',
                'ordering': ['user__email'],
            },
        ),
        migrations.AddField(
            model_name='hostel',
            name='manager',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_hostel', to='hostel.hostelmanager'),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=20)),
                ('room_type', models.CharField(choices=[('single', 'Single Occupancy'), ('double', 'Double Occupancy'), ('triple', 'Triple Occupancy'), ('dormitory', 'Dormitory (Multiple Occupancy)')], max_length=20)),
                ('capacity', models.PositiveIntegerField()),
                ('current_occupancy', models.PositiveIntegerField(default=0)),
                ('rent_per_bed', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hostel.hostel')),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
                'ordering': ['hostel', 'room_number'],
                'unique_together': {('hostel', 'room_number')},
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enroll_number', models.CharField(max_length=30, unique=True)),
                ('registration_number', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1, null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('year_of_study', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('admission_year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('admission_date', models.DateField(blank=True, null=True)),
                ('leaving_date', models.DateField(blank=True, null=True)),
                ('is_active_student', models.BooleanField(default=True, verbose_name='Is Active Student in Institute')),
                ('emergency_contact_name', models.CharField(blank=True, max_length=100, null=True)),
                ('emergency_contact_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('address_line1', models.CharField(blank=True, max_length=200, null=True)),
                ('address_line2', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('pincode', models.CharField(blank=True, max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='director.branch')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='director.course')),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students_profiles', to='director.institute')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Student Profile',
                'verbose_name_plural': 'Student Profiles',
                'ordering': ['institute', 'enroll_number'],
            },
        ),
        migrations.CreateModel(
            name='RoomAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='allocation', to='hostel.hostelapplication')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='hostel.room')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_allocations', to='hostel.student')),
            ],
            options={
                'ordering': ['-start_date', 'student'],
                'unique_together': {('student', 'room', 'start_date')},
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('security_deposit', 'Security Deposit'), ('rent', 'Rent'), ('maintenance_fee', 'Maintenance Fee'), ('other', 'Other Fee')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded'), ('waived', 'Waived')], default='pending', max_length=20)),
                ('due_date', models.DateField()),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('room_allocation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='hostel.roomallocation')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='hostel.student')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['-due_date', 'student'],
            },
        ),
        migrations.AddField(
            model_name='hostelapplication',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hostel_applications', to='hostel.student'),
        ),
        migrations.AlterUniqueTogether(
            name='hostel',
            unique_together={('name', 'institute')},
        ),
    ]
