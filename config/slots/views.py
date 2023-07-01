from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, authentication, serializers, status
from users.authentication import TokenAuthentication
from users.permissions import isTiccCounsellorOrManager
from .serializers import AvailableSlotSerializer, HolidaySerializer, LeaveSerializer
from .models import AvailableSlot, Holiday, Leave, LeaveSlot
from rest_framework.response import Response
from users.models import User
from django.apps import apps
from rest_framework.views import APIView
from django.utils import timezone
from users.permissions import IsTiccCounsellor
from datetime import datetime, timedelta, time
# Create your views here.

Booking = apps.get_model('users', 'Booking')

class AvailableSlotList(generics.ListAPIView):
    serializer_class = AvailableSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        isAvailable = self.request.query_params.get('isAvailable')
        print(start_date, end_date, isAvailable)
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
        slot_id = self.request.query_params.get('slot_id')
        queryset = AvailableSlot.objects.all()
        obj = generics.get_object_or_404(queryset, id=slot_id)
        return obj
    
 

class ListHolidayView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Holiday.objects.all()
        serializer = HolidaySerializer(queryset, many=True)
        return Response(serializer.data)


class CreateHolidayView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]

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
        date = self.request.query_params.get('date')
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
    
     
    
class CreateLeaveView(APIView):

    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    def post(self, request):

        method = request.data.get('method')

        if method == 'by_date':
            date = request.data.get('date')
            slot_ids = AvailableSlot.objects.filter(date=date, isAvailable=True).values_list('id', flat=True)
        elif method == 'by_slot':
            slot_ids = request.data.get('slots')
            slots = AvailableSlot.objects.filter(id__in=slot_ids)
            distinct_dates = slots.values_list('date', flat=True).distinct()
            if len(distinct_dates) > 1:
                return Response({'detail': 'Slots must be on the same date'}, status=status.HTTP_400_BAD_REQUEST)
            date = distinct_dates[0]
        else:
            return Response({'detail': 'Invalid method'}, status=status.HTTP_400_BAD_REQUEST)
    
        counsellor_id = self.request.data.get('counsellor')
        if not counsellor_id:
            return Response({'detail': 'Please provide a counsellor'}, status=400)
        try:
            counsellor = User.objects.get(id=counsellor_id, is_ticc_counsellor=True)
        except User.DoesNotExist:
            return Response({'detail': 'The specified user does not exist or is not a TICC counsellor.'}, status=404)
        
        data = {
            'counsellor': counsellor_id,
            'date': date,
            'slots': slot_ids
        }
        request.data.update(data)
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(slots=slot_ids, counsellor=counsellor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ListLeaveView(APIView):

    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    def get(self, request, *args, **kwargs):

        # Check if counsellor parameter is provided
        counsellor_id = self.request.query_params.get('counsellor')
        leaves = Leave.objects.all()
        if counsellor_id:
            leaves = leaves.filter(counsellor=counsellor_id)
        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated, isTiccCounsellorOrManager]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    def delete(self, request, *args, **kwargs):
        leave_id = self.request.query_params.get('leave_id')
        try: 
            leave = Leave.objects.get(id=leave_id)
        except Leave.DoesNotExist:
            return Response({'detail': 'No leave found for the specified id'}, status=404)
        
        leave_slots = LeaveSlot.objects.filter(leave=leave)
        slot_ids = [leave_slot.slot.id for leave_slot in leave_slots]

        slots = slots = AvailableSlot.objects.filter(id__in=slot_ids)

        isAvailable = True
        if Holiday.objects.filter(date=leave.date).exists():
            isAvailable = False
        for slot in slots:
            slot.capacity += 2
            slot.save()
            slot.isAvailable = isAvailable
        # #send users of booked slots a notification
        # booked_slot  s = Booking.objects.filter(slot=slot)
        # for booked_slot in booked_slots:
        #     user = booked_slot.user
        #     message = "A slot you booked on " + str(slot.date) + " at " + str(slot.time) + " has been cancelled. Please book another slot."
        leave.delete()
        return Response(status=204)

    

class GenerateSlotsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTiccCounsellor]
    authentication_classes = [TokenAuthentication, authentication.SessionAuthentication]
    queryset = AvailableSlot.objects.all()
    serializer_class = AvailableSlotSerializer

    def post(self, request):
        date = request.data.get('date')
        start_time = request.data.get('start_time', 9)
        end_time = request.data.get('end_time', 16)
        capacity = request.data.get('capacity', 4)

        if not date:
            return Response({'detail': 'Please provide a date'}, status=status.HTTP_400_BAD_REQUEST)

        date = datetime.strptime(date, '%Y-%m-%d').date()

        if Holiday.objects.filter(date=date).exists():
            return Response({'detail': 'Slots cannot be generated for a holiday'}, status=status.HTTP_400_BAD_REQUEST)

        if AvailableSlot.objects.filter(date=date).exists():
            return Response({'detail': 'Slots have already been generated for this date'}, status=status.HTTP_400_BAD_REQUEST)

        start_time = time(hour=start_time)
        end_time = time(hour=end_time)

        start_minute = start_time.hour * 60
        end_minute = end_time.hour * 60

        slots = []
        for i in range(start_minute, end_minute, 30):
            start_datetime = datetime.combine(date, start_time) + timedelta(minutes=i)
            end_datetime = datetime.combine(date, start_time) + timedelta(minutes=i + 30)
            slot = AvailableSlot(date=date, start_time=start_datetime, end_time=end_datetime, capacity=capacity, isAvailable=True)
            slots.append(slot)

        try:
            AvailableSlot.objects.bulk_create(slots)
            serializer = AvailableSlotSerializer(slots, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            