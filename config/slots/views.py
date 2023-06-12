from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, authentication, serializers, status
from users.authentication import TokenAuthentication
from users.permissions import isTiccCounsellorOrManager
from .serializers import AvailableSlotSerializer, HolidaySerializer, LeaveSerializer
from .models import AvailableSlot, Holiday, Leave
from rest_framework.response import Response
from users.models import User
from django.apps import apps
# Create your views here.

Booking = apps.get_model('users', 'Booking')

class AvailableSlotList(generics.ListAPIView):
    serializer_class = AvailableSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]

    def get_queryset(self):
        start_date = self.request.data.get('start_date')
        end_date = self.request.data.get('end_date')
        isAvailable = self.request.data.get('isAvailable')
        if start_date and end_date:
            # Perform validation on start_date and end_date if required
            queryset = AvailableSlot.objects.filter(date__range=[start_date, end_date])
        else:
            queryset = AvailableSlot.objects.filter()

        if isAvailable:
            queryset = queryset.filter(isAvailable=isAvailable)
        else:
            queryset = queryset.filter(isAvailable=True)
        
        return queryset
    

class AvailableSlotDetail(generics.RetrieveAPIView):
    serializer_class = AvailableSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]

    def get_object(self):
        slot_id = self.request.data.get('slot_id')
        queryset = AvailableSlot.objects.all()
        obj = generics.get_object_or_404(queryset, id=slot_id)
        return obj
    
 

class CreateListHolidayView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Only allow authenticated users with specific permissions for creating
            return [permissions.IsAuthenticated(), isTiccCounsellorOrManager()]
        else:
            # Allow any user to list holidays
            return [permissions.IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        # Check if date parameter is provided
        date = self.request.data.get('date')
        if date:
            # Retrieve holiday details for the specified date
            try:
                holiday = Holiday.objects.get(date=date)
                serializer = self.get_serializer(holiday)
                return Response(serializer.data)
            except Holiday.DoesNotExist:
                return Response({'detail': 'No holiday found for the specified date'}, status=404)

        # Return list of all holidays
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class DeleteHolidayView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer

    def delete(self, request, *args, **kwargs):
        date = self.request.data.get('date')
        if date:
            try:
                holiday = Holiday.objects.get(date=date)
                holiday.delete()
                #mark the slots as available
                AvailableSlot.objects.filter(date=date).update(isAvailable=True)
                return Response(status=204)
            except Holiday.DoesNotExist:
                return Response({'detail': 'No holiday found for the specified date'}, status=404)
        return Response({'detail': 'Please provide a date'}, status=400)
    
    
class CreateListLeaveView(generics.ListCreateAPIView):
    """
    API view for creating and listing leave instances.

    GET:
    Retrieve leave instances for the specified counsellor or list all leave instances.

    POST:
    Create a new leave instance for the specified counsellor.
    """

    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve leave instances for the specified counsellor or list all leave instances.

        Parameters:
        - counsellor: The ID of the counsellor for whom to retrieve leave instances.

        Returns:
        - If the 'counsellor' parameter is provided:
            - 200 OK with the leave instances for the specified counsellor.
            - 404 Not Found if the specified counsellor does not exist or is not a counsellor.
            - 404 Not Found if no leave instances are found for the specified counsellor.
        - If the 'counsellor' parameter is not provided:
            - The default list view behavior is invoked, returning all leave instances.
        """
        # Check if counsellor parameter is provided
        counsellor_id = self.request.query_params.get('counsellor')

        if counsellor_id:
            try:
                counsellor = User.objects.get(id=counsellor_id)
                if not counsellor.is_ticc_counsellor:
                    return Response({'detail': 'The specified user is not a counsellor'}, status=400)
            except User.DoesNotExist:
                return Response({'detail': 'The specified user does not exist'}, status=404)
            # Retrieve leave details for the specified counsellor
            try:
                leaves = Leave.objects.filter(counsellor=counsellor)
                serializer = self.get_serializer(leaves, many=True)
                return Response(serializer.data)
            except Leave.DoesNotExist:
                return Response({'detail': 'No leave found for the specified counsellor'}, status=404)
        
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new leave instance for the specified counsellor.

        Parameters:
        - counsellor: The ID of the counsellor for whom to create a leave instance.
        - date: The date of the leave instance.
        - description (optional): The description or reason for the leave.

        Returns:
        - 201 Created with the newly created leave instance.
        - 400 Bad Request if the 'counsellor' parameter is missing.
        - 400 Bad Request if a leave instance for the specified counsellor already exists on the provided date.
        - 404 Not Found if the specified user does not exist or is not a TICC counsellor.
        """
        counsellor_id = self.request.data.get('counsellor')
        date = self.request.data.get('date')

        # Check if counsellor parameter is provided
        if not counsellor_id:
            return Response({'detail': 'Counsellor ID is required.'}, status=400)

        # Check if a leave for the specified counsellor already exists on this date
        if Leave.objects.filter(counsellor_id=counsellor_id, date=date).exists():
            return Response({'detail': 'A leave for the specified counsellor already exists on this date.'}, status=400)

        # Check if the specified user is a TICC counsellor
        try:
            counsellor = User.objects.get(id=counsellor_id, is_ticc_counsellor=True)
        except User.DoesNotExist:
            return Response({'detail': 'The specified user does not exist or is not a TICC counsellor.'}, status=404)

        # Create a new leave instance
        leave_data = {
            'counsellor': counsellor_id,
            'date': date,
            'description': self.request.data.get('description', '')
        }
        serializer = self.get_serializer(data=leave_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)


class DeleteLeaveView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    def delete(self, request, *args, **kwargs):
        leave_id = self.request.data.get('leave_id')
        try: 
            leave = Leave.objects.get(id=leave_id)
            leave.delete()
            slots = AvailableSlot.objects.filter(date=leave.date)
            for slot in slots:
                slot.capacity = slot.capacity + 2
                slot.isAvailable = True
                slot.save()
                    # #send users of booked slots a notification
                    # booked_slot  s = Booking.objects.filter(slot=slot)
                    # for booked_slot in booked_slots:
                    #     user = booked_slot.user
                    #     message = "A slot you booked on " + str(slot.date) + " at " + str(slot.time) + " has been cancelled. Please book another slot."
            if not Holiday.objects.filter(date=leave.date).exists():
                AvailableSlot.objects.filter(date=leave.date).update(isAvailable=True)

            return Response(status=204)
        except Leave.DoesNotExist:
            return Response({'detail': 'No leave found for the specified id'}, status=404)

    