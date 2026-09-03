from django.urls import path

from news.views import NewsDetailView, NewsListView

app_name = "news"

urlpatterns = [
    path("", NewsListView.as_view(), name="list"),
    path("<int:pk>/", NewsDetailView.as_view(), name="detail"),
]
