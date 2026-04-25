from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/banks/', include('banks.urls')),
    path('api/rounds/', include('rounds.urls')),
    path('api/poisoning/', include('poisoning.urls')),
    path('api/compliance/', include('compliance.urls')),
    path('api/audit/', include('audit.urls')),
]
