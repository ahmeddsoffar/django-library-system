from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import MemberProfile


class RegisterSerializer(serializers.ModelSerializer):
    ## write only sent from the api not the other way around
    password=serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm=serializers.CharField(write_only=True, required=True)


    class Meta: ## telling the serializer which model to use and which fields to include
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name']
        
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    @transaction.atomic ## as there are 2 models that need to be created user and memberprofile
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data) ## ** here unpack of the dic happened
        MemberProfile.objects.create(user=user)
        return user










# @transaction.atomic
# def create(self, validated_data):
#     validated_data.pop('password_confirm')

#     profile_data = {
#         'phone_number': validated_data.pop('phone_number', ''),
#         'address': validated_data.pop('address', ''),
#     }

#     user = User.objects.create_user(**validated_data)

#     MemberProfile.objects.create(
#         user=user,
#         **profile_data
#     )

#     return user