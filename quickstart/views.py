import re

import goslate
import lyricsgenius
import nltk
from afinn import Afinn
from nltk.corpus import brown
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from nltk.tokenize import word_tokenize
from langdetect import detect
#from sentiment_analysis_spanish import sentiment_analysis
from sentiment_analysis_spanish import sentiment_analysis

from quickstart.serializers import LyricSerializer

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
            language = detect(lyric)
            grades = []
            sentiments = []
            affin_data = Afinn()

            for line in lyric.split("\n"):
                print("validando...")
                sentiment = sentiment_analysis.SentimentAnalysisSpanish()
                line = line.replace('(','').replace(')','')
                first_del_pos = line.find("[")
                second_del_pos = line.find("]")
                final_line = line
                if first_del_pos != second_del_pos:
                    final_line = line.replace(line[first_del_pos:second_del_pos + 1], "")
                if final_line:
                    if language == "en":
                        grades.append(affin_data.score(final_line))
                    elif language == "es":
                        grades.append(sentiment.sentiment(final_line))
                if len(grades) > 0:
                    grades_sum = 0
                    for i in grades:
                        grades_sum += i
                    sentiment_value = grades_sum / len(grades)
                    if language == "en":
                        if sentiment_value >= 0.15:
                            sentiment = "positive"
                            sentiments.append(sentiment)
                        elif sentiment_value < -0.15:
                            sentiment = "negative"
                            sentiments.append(sentiment)
                        else:
                            sentiment = "neutral"
                            sentiments.append(sentiment)
                    elif language == "es":
                        if sentiment_value >= 0.55:
                            sentiment = "positive"
                            sentiments.append(sentiment)
                        elif sentiment_value < 0.35:
                            sentiment = "negative"
                            sentiments.append(sentiment)
                        else:
                            sentiment = "neutral"
                            sentiments.append(sentiment)
                    else:
                        sentiment = "neutral"
                        sentiments.append(sentiment)

            countNegative = sentiments.count('negative')
            countNeutral = sentiments.count('neutral')
            countPositive = sentiments.count('positive')
            feeling = ''
            if countPositive > countNeutral and countPositive > countNegative:
                feeling = 'Feliz'
            elif countNegative > countNeutral and countNegative > countPositive:
                feeling = 'Triste'
            else:
                feeling = 'Neutro'

            final_score = "{0:.2f}".format(sentiment_value * 100)
            data['score'] = final_score
            data['feeling'] = feeling
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


class LevelOfComplexityAPIView(GenericAPIView):
    serializer_class = LyricSerializer

    def post(self, request, *args, **kwargs):
        serializer = LyricSerializer(data=request.data)
        if serializer.is_valid:
            data = request.data
            lyric = data.get('lyric')
            lyrics = lyric.split("\n")
            statistics = {}
            dic = {}  ## diccionario: claves palabras - valores lista de # lineas
            cont = 1  ## contador de lineas
            words = ''
            sents = []
            for text in lyrics:
                words = words + ' ' + text
                sents.append(text)
                exclude = ['(',')',',','[',']',';',':']
                for pal in word_tokenize(text.lower()):
                    if not pal in exclude:
                        if pal in dic:
                            dic[pal].append(cont)
                        else:
                            dic[pal] = [cont]
                cont += 1

            #Calcular Índice de legibilidad de la cancion  (IAL)
            resultNlmp = defNlpw(words.split())
            resultNpxf = defNpxf(sents)
            varIal = 4.71 * resultNlmp + 0.5 * resultNpxf - 21.43
            statistics["IAL"] = varIal

            list_words = []
            for k, v in dic.items():
                repeated = 0
                line = 0
                for value in v:
                    countLine = v.count(value)
                    if countLine > repeated:
                        repeated = countLine
                        line = value
                lineMoreRepeted = {'line': line, 'count': repeated}
                list_words.append({'word': k, 'line': v, 'more_repeated':lineMoreRepeted})

            statistics["list_words"] = list_words

            data = {'analysis': statistics}
            return Response(data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


#Función para calcular NLPW, pasando como parámetro una lista de palabras
def defNlpw(words):
    if len(words)==0:
        return 0
    return sum(len(word) for word in words) / len(words)

#Función para calcular NPXF, pasando como parámetro una lista de sentencias
def defNpxf(sents):
    if len(sents)==0:
        return 0
    return sum(numWords(sent) for sent in sents)/len(sents)

def numWords(sent):
    return len(word_tokenize(' '.join(sent)))