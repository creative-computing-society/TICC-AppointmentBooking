from rest_framework import permissions
from .models import Student


class IsTiccCounsellor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_ticc_counsellor


class IsStudentOrTiccCounsellor(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        user_id = request.data.get('id')
        return user.is_ticc_counsellor or user.student



class isTiccCounsellorOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_ticc_counsellor or user.is_manager

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_ticc_counsellor or user.is_manager
    

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            user.student
            return True
        except Student.DoesNotExist:
            return False