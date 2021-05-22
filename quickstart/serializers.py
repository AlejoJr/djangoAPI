from django.contrib.auth.models import User
from rest_framework import serializers

from quickstart.models import Lyric


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class LyricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lyric
        fields = '__all__'

