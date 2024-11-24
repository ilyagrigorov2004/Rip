
from django.contrib import admin
from django.urls import path
from ConferencesWeb_App import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('Authors/', views.AuthorsList.as_view(), name='Authors_url'),
    path('Author/<int:id>/', views.SingleAuthor.as_view(), name='Author_url'),
    path('Author/<int:id>/imgUpload/', views.AuthorImageUpload.as_view(), name='Author_img_url'),
    path('Author/<int:id>/addToConference/', views.AuthorAdding.as_view(), name='AddAuthor_url'),

    path('Conferences/', views.ConferencesList.as_view(), name='Conferences_url'),
    path('Conference/<int:id>/', views.SingleConference.as_view(), name='Conference_url'),
    path('Conference/<int:id>/form/', views.ConferenceForming.as_view(), name='DeleteConference_url'),
    path('Conference/<int:id>/confirm/', views.ConferenceConfirming.as_view(), name='ConfirmConference_url'),
    
    path('AuthorInConf/<int:conf_id>/<int:author_id>/', views.mm.as_view(), name='AuthorInConf_url'),
    
    path('User/', views.UserLK.as_view(), name='UserLK_url'),
    path('User/register/', views.UserRegistration.as_view(), name='UserRegistration_url'),
    path('User/login/', views.UserLogIn.as_view(), name='UserLogin_url'),
    path('User/logout/', views.UserLogOut.as_view(), name='UserLogout_url'),
]
