from rest_framework import serializers
from .models import User, Student, Booking
from slots.serializers import AvailableSlotSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'is_ticc_counsellor', 'is_ticc_manager', 'password']

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
        fields_to_update = ['roll_number', 'branch', 'admission_year', 'gender']
        for field in fields_to_update:
            if field in validated_data and not getattr(instance, field):
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


# class BookingSerializer(serializers.ModelSerializer):
#     student_email = serializers.EmailField(source='student.user.email', read_only=True)
#     assigned_counsellor_email = serializers.EmailField(source='assigned_counsellor.user.email', read_only=True)
#     slot = AvailableSlotSerializer(read_only=True)
#     class Meta:
#         model = Booking
#         fields = ['id', 'slot', 'student', 'student_email', 'additional_info', 'remarks',  "assigned_counsellor", "assigned_counsellor_email", "is_active"]

class BookingSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source='student.user.email', read_only=True)
    assigned_counsellor_email = serializers.EmailField(source='assigned_counsellor.user.email', read_only=True)
    slot = AvailableSlotSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'slot', 'student', 'student_email', 'additional_info', 'remarks',
                  'assigned_counsellor', 'assigned_counsellor_email', 'is_active']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['student'] = instance.student.id
        representation['assigned_counsellor'] = instance.assigned_counsellor.id if instance.assigned_counsellor else None
        return representation
