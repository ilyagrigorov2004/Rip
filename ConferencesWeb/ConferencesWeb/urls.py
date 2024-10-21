
from django.contrib import admin
from django.urls import path
from ConferencesWeb_App import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Conferences/<int:id>', views.ConferencesController, name='Conferences_url'),
    path('', views.ScientistsController, name = 'main_url'),
    path('Scientist/<int:id>/', views.ScientistDescriptionController, name='Scientist_url'),
]
