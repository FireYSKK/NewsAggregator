from django.urls import path
from . import views

urlpatterns = [
    path('detail/<int:pk>', views.NewsDetailView.as_view(), name='news_detail'),
    path('news/', views.NewsView.as_view(), name='news')
]
