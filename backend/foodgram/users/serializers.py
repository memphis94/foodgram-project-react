from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import Follow, User


class CustomCreateUserSerializers(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(CustomCreateUserSerializers, self).create(validated_data)


class CustomUserSerializers(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    class Meta:
        model = User
        fields = '__all__'
