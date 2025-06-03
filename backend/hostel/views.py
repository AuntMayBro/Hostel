from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from hostel.models import ( 
    Room, Hostel, HostelApplication, HostelManager, Student, ApplicationStatus
)
from hostel.serializers import (
    RoomSerializer, HostelManagerSerializer, HostelApplicationSerializer
)

class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        hostel_id = self.request.query_params.get('hostel_id')
        
        if hostel_id:
            try:
                hostel = Hostel.objects.get(pk=hostel_id)
                if not (user.is_superuser or 
                        (hasattr(user, 'director_profile') and hostel.director == user.director_profile) or
                        (hasattr(user, 'hostelmanager_profile') and hostel.manager == user.hostelmanager_profile)):
                    raise PermissionDenied("You cannot view rooms for this hostel.")
                return Room.objects.filter(hostel=hostel).select_related('hostel')
            except Hostel.DoesNotExist:
                return Room.objects.none() # Or raise NotFound
        
        if user.is_superuser:
            return Room.objects.all().select_related('hostel')
        if hasattr(user, 'director_profile'):
            return Room.objects.filter(hostel__institute=user.director_profile.institute).select_related('hostel')
        if hasattr(user, 'hostelmanager_profile') and user.hostelmanager_profile.managed_hostel:
             return Room.objects.filter(hostel=user.hostelmanager_profile.managed_hostel).select_related('hostel')
        return Room.objects.none()


    def perform_create(self, serializer):
        user = self.request.user
        hostel = serializer.validated_data['hostel']

        if not (user.is_superuser or
                (hasattr(user, 'director_profile') and hostel.director == user.director_profile) or
                (hasattr(user, 'hostelmanager_profile') and hostel.manager == user.hostelmanager_profile)):
            raise PermissionDenied("You are not authorized to add rooms to this hostel.")
        
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all().select_related('hostel')
    serializer_class = RoomSerializer
    # permission_classes = [IsAuthenticated, IsDirectorOrManagerForHostelObject]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class HostelManagerListCreateView(generics.ListCreateAPIView):
    serializer_class = HostelManagerSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return HostelManager.objects.all().select_related('user', 'institute', 'managed_hostel')
        if hasattr(user, 'director_profile'):
            return HostelManager.objects.filter(institute=user.director_profile.institute).select_related('user', 'institute', 'managed_hostel')
        return HostelManager.objects.none()

    def perform_create(self, serializer):
        user = self.request.user 

        manager_user_instance = serializer.validated_data['user'] 
        institute_instance = serializer.validated_data['institute']

        if not hasattr(user, 'director_profile') and not user.is_superuser:
            raise PermissionDenied("Only Directors or Superusers can assign Hostel Managers.")

        if hasattr(user, 'director_profile'):
            if user.director_profile.institute != institute_instance:
                raise PermissionDenied("You can only assign managers within your own institute.")
        
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class HostelManagerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HostelManager.objects.all().select_related('user', 'institute', 'managed_hostel')
    serializer_class = HostelManagerSerializer
    # permission_classes = [IsAuthenticated] 

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not user.is_superuser and hasattr(user, 'director_profile'):
            if obj.institute != user.director_profile.institute:
                raise PermissionDenied("You do not have permission to manage this Hostel Manager.")
        elif not user.is_superuser:
            raise PermissionDenied("Permission denied.")
        return obj
    
    def perform_destroy(self, instance):
        if hasattr(instance, 'managed_hostel') and instance.managed_hostel:
            hostel = instance.managed_hostel
            hostel.manager = None
            hostel.save(update_fields=['manager'])
        instance.delete()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class HostelApplicationViewSet(viewsets.ModelViewSet):
    queryset = HostelApplication.objects.all().select_related(
        'student__user', 'institute', 'preferred_hostel', 'reviewed_by'
    )
    serializer_class = HostelApplicationSerializer
    # permission_classes = [IsAuthenticated]

    # def get_permissions(self):
    #     if self.action == 'create':
    #         self.permission_classes = [IsAuthenticated, IsStudentRole]
    #     elif self.action in ['update', 'partial_update']:
    #         # Owner (student for certain fields), or Director/Manager/Admin for status changes
    #         self.permission_classes = [IsAuthenticated, IsOwnerOrAdminForApplication] 
    #     elif self.action == 'destroy':
    #         self.permission_classes = [IsAuthenticated, IsAdminUser] # Or Director
    #     elif self.action in ['list', 'retrieve']:
    #         self.permission_classes = [IsAuthenticated]
    #     else:
    #         self.permission_classes = [IsAuthenticated] # Default
    #     return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return HostelApplication.objects.none()

        if user.is_superuser or hasattr(user, 'director_profile'):
            if hasattr(user, 'director_profile'):
                return self.queryset.filter(institute=user.director_profile.institute)
            return self.queryset 
        
        if hasattr(user, 'hostelmanager_profile') and user.hostelmanager_profile.managed_hostel:
            return self.queryset.filter(preferred_hostel__institute=user.hostelmanager_profile.institute)

        if hasattr(user, 'student_profile'):
            return self.queryset.filter(student=user.student_profile)
        
        return HostelApplication.objects.none()

    def perform_create(self, serializer):
        user = self.request.user 
        serializer.save(
            student=user.student_profile, 
            institute=user.student_profile.institute,
            course_at_application=user.student_profile.course,
            branch_at_application=user.student_profile.branch,
            status=ApplicationStatus.PENDING,
            submitted_at=timezone.now()
        )

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context