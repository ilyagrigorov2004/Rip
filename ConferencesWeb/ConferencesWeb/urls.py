
from django.contrib import admin
from django.urls import path
from ConferencesWeb_App import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Conferences/<int:id>', views.ConferencesController, name='Conferences_url'),
    path('', views.AuthorsController, name = 'main_url'),
    path('Author/<int:id>/', views.AuthorDescriptionController, name='Author_url'),
]
