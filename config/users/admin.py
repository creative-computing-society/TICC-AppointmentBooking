from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Booking


@admin.register(User)
class CustomUserView(UserAdmin):
    list_display = ('email', 'is_staff','is_ticc_counsellor', 'is_ticc_manager', 'is_superuser')
    list_filter = ('is_staff', 'is_ticc_counsellor', 'is_ticc_manager', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('email', 'password', 'full_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_ticc_counsellor', 'is_ticc_manager', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'full_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_ticc_counsellor', 'is_ticc_manager', 'is_superuser')}),
    ) 

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        instance = form.instance
        if not change and not instance.is_ticc_counsellor:
            student, created = Student.objects.get_or_create(user=instance)
            if created:
                student.save()



@admin.register(Student)
class CustomStudentView(admin.ModelAdmin):
    list_display = ['user', 'roll_number', 'branch', 'admission_year', 'gender']
    list_filter = ['branch', 'admission_year', 'gender']
    search_fields = ['user__email', 'roll_number']
    readonly_fields = ['user']
    fieldsets = [
        ('User Information', {'fields': ['user']}),
        ('Student Details', {'fields': ['roll_number', 'branch', 'admission_year', 'gender']}),
    ]

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['roll_number', 'branch', 'admission_year', 'gender']
        return self.readonly_fields

    
@admin.register(Booking)
class CustomBookingAdmin(admin.ModelAdmin):
    list_display = ['student', 'slot', 'remarks', 'is_active', 'token']
    list_filter = ['slot__date', 'is_active']
    readonly_fields = ['token']
    search_fields = ['student__user__email', 'slot__date']


    actions = ['cancel_selected_bookings']

    def cancel_selected_bookings(self, request, queryset):
        for booking in queryset:
            booking.remarks = 'Cancelled by admin'
            booking.save()

    cancel_selected_bookings.short_description = 'Cancel selected bookings'
