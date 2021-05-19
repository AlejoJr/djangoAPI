from django.shortcuts import render
import requests
import json
from afinn import Afinn, afinn
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
import goslate
from rest_framework import permissions
#from quickstart.serializers import UserSerializer, GroupSerializer
from quickstart.serializers import UserSerializer

class UserAPIView(APIView):

    def get(self,request):
            users = User.objects.all()
            users_serializer = UserSerializer(users,many=True)
            return Response(users_serializer.data)

class LyricsAPIView(APIView):

    def get(self,request, *args, **kwargs):
        if kwargs.get("artist", None) and  kwargs.get("songTitle", None) is not None:
            artist =  kwargs["artist"]
            songTitle =  kwargs["songTitle"]
            url = 'https://api.lyrics.ovh/v1/' + artist + '/' + songTitle
            response = requests.get(url)
            json_data = json.loads(response.content)
            return Response(json_data)

class AfinnAPIView(APIView):

    def get(self,request, *args, **kwargs):
        if kwargs.get("lyrics", None) is not None:
            lyrics =  kwargs["lyrics"]
            afinn = Afinn()
            gs = goslate.Goslate()
            word = gs.translate(lyrics, 'en')
            resultAfinn = afinn.score(word)
            # Calculate word cound of lyric
            word_count = len(word.split())
            # Calculate comparative score
            comparative_score = resultAfinn / word_count
            finalScore = "{0:.2f}".format(comparative_score * 100)
            response = '{ "score":'+finalScore+'}'
            json_data = json.loads(response)
            return Response(json_data)

