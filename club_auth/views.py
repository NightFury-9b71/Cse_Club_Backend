from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from .models import CustomUser

# Register view to create a new user and return the JWT token
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()  # Save the user

        # Create JWT token for the newly registered user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "message": "User registered successfully",
            "access_token": access_token  # Send the token in the response
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login view to authenticate and return a JWT token
@api_view(['POST'])
def login(request):
    studentId = request.data.get('studentId')
    password = request.data.get('password')

    # Authenticate the user using the provided credentials
    user = authenticate(username=str(studentId), password=password)

    if user:
        # Generate JWT token for the authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "message": "Login successful",
            "access_token": access_token  # Send the token in the response
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid studentId or password"}, status=status.HTTP_400_BAD_REQUEST)


# Check if the user is authenticated or not
@api_view(['GET'])
def check(request):
    if request.user.is_authenticated:
        return Response({"message": "Authenticated user"})
    else:
        return Response({"message": "Unauthenticated user"}, status=401)
