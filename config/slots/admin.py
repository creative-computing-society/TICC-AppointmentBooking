from django.contrib import admin
from .models import AvailableSlot, Leave, Holiday
# Register your models here.

admin.site.site_header = "TICC Admin"
admin.site.site_title = "TICC Admin Portal"
admin.site.index_title = "Welcome to TICC Portal"

@admin.register(AvailableSlot)
class CustomSlotsView(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'slots_booked', 'isAvailable')
    list_filter = ('date', 'isAvailable')
    search_fields = ('date',)
    ordering = ('date',)


@admin.register(Holiday)
class CustomHolidayView(admin.ModelAdmin):
    list_display = ('date','description')
    list_filter = ('date',)
    search_fields = ('date',)
    ordering = ('date',)


@admin.register(Leave)
class CustomLeaveView(admin.ModelAdmin):
    list_display = ('counsellor', 'date','description', )
    list_filter = ('date',)
    search_fields = ('counsellor__email', 'date',)
    ordering = ('-date',)