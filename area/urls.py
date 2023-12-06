from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('polls.urls', namespace="polls")),
    path("", include("allauth.urls")),
    # path("", include("django_cypress.urls")),
]
