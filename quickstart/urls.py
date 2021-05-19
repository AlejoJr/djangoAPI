from django.urls import path

from quickstart.views import UserAPIView, LyricsAPIView, AfinnAPIView

urlpatterns = [
    path('usuario/', UserAPIView.as_view(), name = 'usuario_api'),
    path('lyrics/<str:artist>/<str:songTitle>/', LyricsAPIView.as_view(), name = 'lyrics_api'),
    path('afinn/<str:lyrics>/', AfinnAPIView.as_view(), name='afinn_api')
]