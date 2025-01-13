from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('genstat/',views.genstat, name='genstat'),
    path('relev/', views.relev, name='relev'),
    path('geo/', views.geo, name='geo'),
    path('skills/', views.skills, name='skills'),
    path('last/', views.latest_vacancies, name='last'),
]