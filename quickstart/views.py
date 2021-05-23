import re
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
from google_trans_new import google_translator

from quickstart.serializers import LyricSerializer


class LyricsAPIView(APIView):
    """
        get:
        Return the lyrics of the song consulted by artist and title
        """
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
    """
            post:
            Returns the sentiment analysis Afinn of the song
            """
    serializer_class = LyricSerializer

    def post(self, request, *args, **kwargs):
        serializer = LyricSerializer(data=request.data)
        if serializer.is_valid:
            data = request.data
            lyric = data.get('lyric')
            sentiment = ''
            affin_data = Afinn()
            translator = google_translator()
            language = detect(lyric)

            if language == "en":
                resultAfinn = affin_data.score(lyric)
                # Palabras por letra
                word_count = len(lyric.split())
            elif language == "es":
                translation = translator.translate(text=lyric, lang_tgt='en', lang_src='auto')
                resultAfinn = affin_data.score(translation)
                # Palabras por letra
                word_count = len(translation.split())

            # Comparativa score
            comparative_score = resultAfinn / word_count

            formatScore = "{0:.2f}".format(comparative_score * 100)
            finalScore = float(formatScore)

            if -4 <= finalScore <= -1:
                sentiment = 'Desanimado'
            elif -8 <= finalScore <= -4:
                sentiment = 'Triste'
            elif finalScore < -8:
                sentiment = 'Melancólico'
            elif -1 <= finalScore <= 1:
                sentiment = 'Normal'
            elif 1 <= finalScore <= 4:
                sentiment = 'Felíz'
            elif 4 <= finalScore <= 8:
                sentiment = 'Alegre'
            elif finalScore > 8:
                sentiment = 'Fenomenal'

            data['score'] = finalScore
            data['feeling'] = sentiment
            serializer = LyricSerializer(data)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class AnalyticsAPIView(GenericAPIView):
    """
    post:
    Returns word analysis: most frequent, most frequent probability, lexicon size, unique words and list words
    """
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
            i = 0
            for k, v in words.items():
                i += 1
                list_words.append({'text': k, 'value': v})
                if i == 20:
                    break
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
    """
        post:
        Returns Song readability index (IAL) and most repeated words on the same line
        """
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
                exclude = ['(', ')', ',', '[', ']', ';', ':']
                for pal in word_tokenize(text.lower()):
                    if not pal in exclude:
                        if pal in dic:
                            dic[pal].append(cont)
                        else:
                            dic[pal] = [cont]
                cont += 1

            # Calcular Índice de legibilidad de la cancion  (IAL)
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
                list_words.append({'word': k, 'line': v, 'more_repeated': lineMoreRepeted})

            statistics["list_words"] = list_words

            data = {'analysis': statistics}
            return Response(data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class DetectWordTypesAPIView(GenericAPIView):
    """
    post:
    Returns the tag marked by each word as adjective, verbs, pronouns, etc.
    """
    serializer_class = LyricSerializer

    def post(self, request, *args, **kwargs):
        serializer = LyricSerializer(data=request.data)
        if serializer.is_valid:
            data = request.data
            lyric = data.get('lyric')
            statistics = {}
            tags = {}
            words = {}
            tokenLyric = nltk.word_tokenize(lyric)
            wordTag = nltk.pos_tag(tokenLyric)
            for w, t in wordTag:
                if t in tags:
                    tags[t] += 1
                else:
                    tags[t] = 1
                if w in words:
                    if t not in words[w]:
                        words[w].append(t)
                else:
                    words[w] = [t]

            count_tags = []
            word_tags = []

            tags = {k: v for k, v in sorted(tags.items(), key=lambda item: item[1], reverse=True)}
            for k, v in tags.items():
                count_tags.append({'tag': k, 'count': v})

            words = {k: v for k, v in sorted(words.items(), key=lambda item: len(item[1]), reverse=True)}

            for k, v in words.items():
                word_tags.append({'word': k, 'tags': v})

            statistics["count_tags"] = count_tags
            statistics["word_tags"] = word_tags

            data = {'analysis': statistics}
            return Response(data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


# Función para calcular NLPW, pasando como parámetro una lista de palabras
def defNlpw(words):
    if len(words) == 0:
        return 0
    return sum(len(word) for word in words) / len(words)


# Función para calcular NPXF, pasando como parámetro una lista de sentencias
def defNpxf(sents):
    if len(sents) == 0:
        return 0
    return sum(numWords(sent) for sent in sents) / len(sents)


def numWords(sent):
    return len(word_tokenize(' '.join(sent)))
