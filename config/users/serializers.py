from rest_framework import serializers
from .models import User, Student, Booking
from slots.serializers import AvailableSlotSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'is_ticc_counsellor', 'is_ticc_manager', 'password']
        read_only_fields = ['is_ticc_counsellor', 'is_ticc_manager']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        # Remove 'email' field from validated_data
        validated_data.pop('email', None)
        return super().update(instance, validated_data)



class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'roll_number', 'branch', 'admission_year', 'gender',]# 'appointments']

    user = UserSerializer(read_only=True)  # Use read_only=True to prevent user creation/update

    def update(self, instance, validated_data):

        # Update student fields if they are not already present
        fields_to_update = ['roll_number', 'admission_year', 'gender']
        for field in fields_to_update:
            if field in validated_data and not getattr(instance, field):
                setattr(instance, field, validated_data[field])
        #allow student to update branch even if it is already present
        if 'branch' in validated_data:
            setattr(instance, 'branch', validated_data['branch'])
        instance.save()
        return instance


class BookingSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source='student.user.email', read_only=True)
    student_name = serializers.CharField(source='student.user.full_name', read_only = True)
    assigned_counsellor_name = serializers.CharField(source='assigned_counsellor.full_name')
    slot = AvailableSlotSerializer(read_only=True)
    user_id = serializers.IntegerField(source='student.user.id', read_only=True)
    phone_number = serializers.CharField(source='student.user.phone_number', read_only=True)

    class Meta:
        model = Booking
        fields = ['user_id', 'id', 'slot', 'student', 'student_email', 'student_name', 'phone_number', 'additional_info', 'remarks',
                  'assigned_counsellor', 'assigned_counsellor_name', 'is_active'] 
    