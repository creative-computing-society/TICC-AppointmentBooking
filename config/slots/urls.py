from django.urls import path, include
from . import views

urlpatterns = [
    path('listslots/', views.AvailableSlotList.as_view(), name='available-slots'),
    path('slotdetails/', views.AvailableSlotDetail.as_view(), name = 'slot-details'),
    path('holidays/list/', views.ListHolidayView.as_view(), name='holidays'),
    path('holidays/add/', views.CreateHolidayView.as_view(), name='create-holidays'),
    path('holidays/delete/', views.DeleteHolidayView.as_view(), name='update-holidays-delete'),
    path('leaves/list/', views.ListLeaveView.as_view(), name='leaves'),
    path('leaves/delete/', views.DeleteLeaveView.as_view(), name='update-leaves-delete'),
    path('leaves/add/', views.CreateLeaveView.as_view(), name='create-leaves'),
]
