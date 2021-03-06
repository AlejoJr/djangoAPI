from django.urls import path

from quickstart.views import  LyricsAPIView, AfinnAPIView, AnalyticsAPIView, LevelOfComplexityAPIView,\
    DetectWordTypesAPIView

urlpatterns = [

    path('lyrics/<str:artist>/<str:song>/', LyricsAPIView.as_view(), name = 'lyrics_api'),
    path('afinn/', AfinnAPIView.as_view(), name='afinn_api'),
    path('analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    path('complexity/', LevelOfComplexityAPIView.as_view(), name='complexity'),
    path('typeWords/', DetectWordTypesAPIView.as_view(), name='typeWords')
]