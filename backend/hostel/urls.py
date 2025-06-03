# hostel/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoomListCreateView,
    RoomDetailView,
    HostelManagerListCreateView,
    HostelManagerDetailView,
    HostelApplicationViewSet,
)

router = DefaultRouter()
router.register(r'applications', HostelApplicationViewSet, basename='hostelapplication')

urlpatterns = [
    # Room's Url
    path('create-room/', RoomListCreateView.as_view(), name='room-list-create'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),

    # Manager's Url
    path('create-manager/', HostelManagerListCreateView.as_view(), name='hostelmanager-list-create'),
    path('manager/<int:pk>/', HostelManagerDetailView.as_view(), name='hostelmanager-detail'),

    # Hostel Application's Url
    path('', include(router.urls)),

]
