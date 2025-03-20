from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login view to authenticate and return a JWT token
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    studentId = request.data.get('studentId')
    password = request.data.get('password')

    # Authenticate the user using the provided credentials
    user = authenticate(username=str(studentId), password=password)

    if user:
        # Generate JWT token for the authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Prepare user data to send with the response
        user_data = {
            "studentId": user.studentId,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "bio": user.bio,
            "year": user.year,
            "semester": user.semester,
            "interests": user.interests,
            "skills": user.skills,
            "github": user.github,
            "linkedin": user.linkedin,
            "avatar": user.avatar.url if user.avatar else None  # Return avatar URL if exists
        }

        return Response({
            "message": "Login successful",
            "access_token": access_token,  # Send the token in the response
            "refresh_token": str(refresh),  # Include refresh token for logout
            "user": user_data  # Include user data in the response
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid studentId or password"}, status=status.HTTP_400_BAD_REQUEST)


# Logout view to blacklist the refresh token
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()  # Blacklist the token to prevent reuse

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# Check if the user is authenticated or not
@api_view(['GET'])
def check(request):
    if request.user.is_authenticated:
        return Response({"message": "Authenticated user"})
    else:
        return Response({"message": "Unauthenticated user"}, status=401)
