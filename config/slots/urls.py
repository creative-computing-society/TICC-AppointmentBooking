from django.urls import path, include
from . import views

urlpatterns = [
    path('listslots/', views.AvailableSlotList.as_view(), name='available-slots'),
    path('slotdetails/', views.AvailableSlotDetail.as_view(), name = 'slot-details'),
    path('holidays/createlist/', views.CreateListHolidayView.as_view(), name='holidays'),
    path('holidays/delete/', views.DeleteHolidayView.as_view(), name='update-holidays-delete'),
    path('leaves/createlist/', views.CreateListLeaveView.as_view(), name='leaves'),
    path('leaves/delete/', views.DeleteLeaveView.as_view(), name='update-leaves-delete')
]
