from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Set the password using set_password method
        if avatar:
            user.avatar = avatar
        user.save()  # Save the user instance with the hashed password
        return user
    

    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['studentId', 'name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create(
            studentId=validated_data['studentId'],
            name=validated_data['name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user
