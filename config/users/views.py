from rest_framework import generics, status, permissions, authentication
from .authentication import TokenAuthentication
from rest_framework.response import Response
from .models import User, Student, Booking
from .serializers import UserSerializer, StudentSerializer, BookingSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, NotFound
from .permissions import IsTiccCounsellor, IsStudent
from slots.models import AvailableSlot
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .tasks import send_booking_confirmation_email
from django.utils import timezone

class UserList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTiccCounsellor]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
   
    def get_object(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')
        # Allow the user to access their own details
        if not user_id or user.id == int(user_id):
            return user
        else :
            # Allow ticc_counsellor users to access user details
            if user.is_ticc_counsellor:
                queryset = self.filter_queryset(self.get_queryset())
                obj = get_object_or_404(queryset, id=user_id)
                self.check_object_permissions(self.request, obj)
                return obj
        raise PermissionDenied("You are not authorized to access this resource.")
    

    def check_object_permissions(self, request, obj):
        user = request.user
        # Allow the user to access their own details
        if user == obj:
            return
        # Allow ticc_counsellor users to access user details
        if user.is_ticc_counsellor:
            return
        raise PermissionDenied("You are not authorized to access this resource.")




class StudentList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTiccCounsellor]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer




class StudentDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_object(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')

        if not user_id or user.id == int(user_id):
            try:
                return user.student
            except Student.DoesNotExist:
                return Response({"detail": "Student details do not exist for the mentioned user."}, status=status.HTTP_404_NOT_FOUND)
        else :
            if user.is_ticc_counsellor:
                queryset = self.filter_queryset(self.get_queryset())
                obj = get_object_or_404(queryset, user_id=user_id)
                self.check_object_permissions(self.request, obj)
                return obj
            
        raise PermissionDenied("You are not authorized to access this resource.")

    def check_object_permissions(self, request, obj):
        user = request.user
        student = obj

        # Allow the user to access their own student details
        if hasattr(user, 'student') and user.student == student:
            return

        # Allow ticc_counsellor users to access student details
        if user.is_ticc_counsellor:
            return

        raise PermissionDenied("You are not authorized to access this resource.")

 

class StudentUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    authentication_classes = [TokenAuthentication]
    serializer_class = StudentSerializer

    def get_object(self):
        user = self.request.user
        try:
            student = user.student
            return student
        except Student.DoesNotExist:
            raise NotFound("Student details do not exist for the current user.")

    def put(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)



class TiccCounsellorList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTiccCounsellor]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = User.objects.filter(is_ticc_counsellor=True)
    serializer_class = UserSerializer


class ListBookingsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')
        is_active = self.request.query_params.get('is_active')
        date = self.request.query_params.get('date')
        
        if user.is_ticc_counsellor:
            queryset = Booking.objects.all()
            if user_id is not None:
                #check if the user_id is a student
                try:
                    student = Student.objects.get(user_id=user_id)
                except Student.DoesNotExist:
                    raise NotFound("Student details do not exist for the mentioned user.")
                queryset = queryset.filter(student__user_id=user_id)
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)
            if date is not None:
                queryset = queryset.filter(slot__date=date)
        else:
            if user_id and user.id != int(user_id):
                raise PermissionDenied("You are not authorized to access bookings of other users.")
            queryset = Booking.objects.filter(student=user.student)
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)
            if date is not None:
                queryset = queryset.filter(slot__date=date)

        return queryset

    
class RetrieveBookingView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    serializer_class = BookingSerializer

    def get_object(self):
        user = self.request.user
        booking_id = self.request.query_params.get('booking_id')  # Assuming you pass the booking ID in the URL
        if not booking_id:
            raise NotFound("Booking ID not provided.")
        try:
            if user.is_ticc_counsellor:
                booking = Booking.objects.get(id=booking_id)
            else:
                booking = Booking.objects.get(id=booking_id, student=user.student)
                if not booking or booking==None:
                    raise NotFound("Booking not found or Booking doesn't belong to the user.")
        except Booking.DoesNotExist:
            raise NotFound("Booking not found.")

        return booking
    


class CreateBookingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        student = user.student
        slot_id = request.data.get('slot_id')
        additional_info = request.data.get('additional_info')

        try:
            slot = AvailableSlot.objects.get(id=slot_id)
        except AvailableSlot.DoesNotExist:
            return Response({'detail': 'Slot not found.'}, status=status.HTTP_404_NOT_FOUND)
        if slot.capacity == slot.slots_booked or not slot.isAvailable:
            return Response({'detail': 'Slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the student already has an appointment for the slot
        if student.bookings.filter(slot=slot, is_active=True).exists() or student.bookings.filter(slot__date=slot.date, is_active=True).exists():
            return Response({'detail': 'You already have an appointment today.'}, status=status.HTTP_400_BAD_REQUEST)
        # Create the booking
        booking = Booking(student=student, slot=slot, additional_info=additional_info, is_active=True)
        booking.save()
        
        # Increment the slots_booked count for the slot
        slot.slots_booked += 1
        if slot.slots_booked == slot.capacity:
            slot.isAvailable = False
        slot.save()
        
        serializer = self.get_serializer(booking)
        print(serializer.data)
        slot_date = booking.slot.date.strftime('%A, %B %d')
        slot_start_time = booking.slot.start_time.strftime('%I:%M %p')
        context = {
        'student_name': booking.student.user.full_name,
        'slot_date': slot_date,
        'slot_start_time': slot_start_time,
        }
        send_booking_confirmation_email.delay(student.user.email, context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class CancelBookingView(APIView):
    permissions_classes = [permissions.IsAuthenticated, IsStudent]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    serializer_class = BookingSerializer

    def delete(self, request, *args, **kwargs):
        user = request.user
        booking_id = request.query_params.get('booking_id')
        
        # Check if the booking exists and belongs to the student
        try:
            booking = Booking.objects.get(id=booking_id, student=user.student)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not booking.is_active:
            return Response({'detail': 'Booking is already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.is_active = False
        booking.remarks = "Cancelled by student"
        booking.save()
        # Decrement the slots_booked count for the slot
        slot = booking.slot
        slot.slots_booked -= 1
        if slot.slots_booked < slot.capacity:
            slot.isAvailable = True
        slot.save()

        return Response({'detail': 'Booking cancelled successfully.'}, status=status.HTTP_204_NO_CONTENT)


class UpdateBookingView(APIView):
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsTiccCounsellor]

    def patch(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = {}
        for field in ['remarks', 'assigned_counsellor', 'is_active']:
            if field in request.data:
                data[field] = request.data[field]

        serializer = BookingSerializer(booking, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class emailBookingCancellation(APIView):
    def get(self, request, booking_token):
        booking = Booking.objects.get(token=booking_token)
        booking.is_active = False
        booking.remarks = "Cancelled by student"
        booking.save()
        # Decrement the slots_booked count for the slot
        slot = booking.slot
        slot.slots_booked -= 1
        if slot.slots_booked < slot.capacity:
            slot.isAvailable = True
        slot.save()

        return Response({'detail': 'Booking cancelled successfully.'}, status=status.HTTP_204_NO_CONTENT)
    


class SearchView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsTiccCounsellor]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]

    def get(self, request):
        search_word = request.query_params.get('searchWord', '')

        # Search for students, users, and roll numbers
        students = Student.objects.filter(user__email__icontains=search_word) | \
                   Student.objects.filter(user__full_name__icontains=search_word) | \
                   Student.objects.filter(roll_number__icontains=search_word)

        # Limit the number of results to 20
        students = students[:20]

        # Serialize the results
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        
        