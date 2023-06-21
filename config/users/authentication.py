from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status, permissions
from .serializers import UserSerializer, StudentSerializer

class TokenAuthentication(BaseTokenAuthentication):
    """
    Extend TokenAuthentication to support custom token header
    """
    keyword = 'Bearer'



class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            user_serializer = UserSerializer(user)
            try:
                student_serializer = StudentSerializer(user.student)
            except:
                return Response({
                'user': user_serializer.data,
                'token': token.key
                })
            return Response({
                'user': user_serializer.data,
                'student': student_serializer.data,
                'token': token.key
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class UserCreationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user)
            student_serializer = StudentSerializer(user.student)
            return Response({
                'user': user_serializer.data,
                'student': student_serializer.data,
                'token': token.key
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    

class UserUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'user_id': user.id}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)