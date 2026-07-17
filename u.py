
from django.urls import path
from .v import rg,lg, cv,sv, dv, br, vp, hr
urlpatterns = [
    path('auth/register/', rg), path('auth/login/', lg), path('villas/', cv), path('villas/search/', sv), path('villas/<int:pk>/', dv), path('reservations/', br),path('payments/verify/', vp),path('reservations/history/', hr),]