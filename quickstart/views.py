import re

import goslate
import lyricsgenius
import nltk
from afinn import Afinn
from django.contrib.auth.models import User
from nltk.corpus import brown
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# from quickstart.serializers import UserSerializer, GroupSerializer
from quickstart.serializers import UserSerializer, LyricSerializer





class LyricsAPIView(APIView):

    def get(self, request, *args, **kwargs):
        if kwargs.get("artist", None) and kwargs.get("song", None) is not None:
            artist = kwargs["artist"]
            song_title = kwargs["song"]
            genius_client = lyricsgenius.Genius("KH8e_WL73pHpuUEbukZ_9Ubp4qzff6rZFsLw6Q2FgNWsSKnT309zE7IrlpJDDaZJ")
            genius_client.verbose = False
            genius_song = None
            data = {'artist': artist, 'title': song_title}
            try:
                genius_song = genius_client.search_song(song_title, artist)
            except:
                pass
            if genius_song and genius_song != "Specified song does not contain lyrics. Rejecting.":
                if genius_song.lyrics:
                    data['lyric'] = genius_song.lyrics

            serializer = LyricSerializer(data)
            return Response(serializer.data)
        else:
            return Response({'errors': ['bad request']}, status=status.HTTP_400_BAD_REQUEST)


class AfinnAPIView(GenericAPIView):
    serializer_class = LyricSerializer

    def post(self, request, *args, **kwargs):
        serializer = LyricSerializer(data=request.data)
        if serializer.is_valid:
            data = request.data
            lyric = data.get('lyric')
            afinn = Afinn()
            first_del_pos = lyric.find("[")
            second_del_pos = lyric.find("]")
            final_line = lyric
            if first_del_pos != second_del_pos:
                final_line = lyric.replace(lyric[first_del_pos:second_del_pos + 1], "")

            gs = goslate.Goslate()
            word = gs.translate(final_line, 'en')
            result_afinn = afinn.score(word)
            # Calculate word cound of lyric
            word_count = len(word.split())
            # Calculate comparative score
            comparative_score = result_afinn / word_count
            final_score = "{0:.2f}".format(comparative_score * 100)
            data['score'] = final_score
            serializer = LyricSerializer(data)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class AnalyticsAPIView(GenericAPIView):
    serializer_class = LyricSerializer

    def post(self, request, *args, **kwargs):
        serializer = LyricSerializer(data=request.data)
        sents = brown.tagged_sents(tagset='universal')
        if serializer.is_valid:
            data = request.data
            lyric = data.get('lyric')
            lyrics = lyric.split("\n")
            split_text_cleaned = []
            words = {}
            for text in lyrics:
                split_text = text.split()
                stop_words = []

                for word in split_text:
                    if (word.lower() not in stop_words) and (word[0] != "[") \
                            and (word[len(word) - 1] != "]") and word == re.sub(r"[^a-zA-Z0-9]", '', word):
                        split_text_cleaned.append(word.lower())
                        if word.lower() in words:
                            words[word.lower()] += 1
                        else:
                            words[word.lower()] = 1
            words = {k: v for k, v in sorted(words.items(), key=lambda item: item[1], reverse=True)}
            list_words = []
            for k, v in words.items():
                list_words.append({'word': k, 'number': v})
            statistics = {}
            freq_dist = nltk.FreqDist(split_text_cleaned)
            statistics["most_frequent"] = freq_dist.max()
            statistics["most_frequent_prob"] = freq_dist.freq(freq_dist.max())
            lexicon = freq_dist.keys()
            statistics["lexicon_size"] = len(lexicon)
            unique_words = freq_dist.hapaxes()
            statistics["unique_words"] = len(unique_words)
            statistics["list_words"] = list_words
            data = {'analysis': statistics}


            return Response(data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
