from rest_framework import serializers
from .models import CustomUser  # Import the new user model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'studentId', 'password', 'name', 'role', 'email', 'bio', 
            'year', 'semester', 'interests', 'skills', 'github', 
            'linkedin', 'avatar'
        ]
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is not exposed
            'studentId': {'required': True},  # Student ID is required
        }

    def create(self, validated_data):
        avatar = validated_data.pop('avatar', None)  # Handle avatar upload
        password = validated_data.pop('password')  # Pop the password from validated_data
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)  # Set the password using set_password method
        if avatar:
            user.avatar = avatar
        user.save()  # Save the user instance with the hashed password
        return user