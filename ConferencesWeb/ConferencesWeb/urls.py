from django.contrib import admin
from django.urls import include, path
from ConferencesWeb_App import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

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

    path('Attribute/add/', views.newAttribute.as_view(), name='Attribute_url'), 
    path('Attribute/<int:id>/', views.Attribute_by_id.as_view(), name='Attribute_by_id_url'),
    path('Attribute/<int:author_id>/<int:attr_id>/addAuthorsAttr/', views.Attr_Author.as_view(), name='AttributeAuthor_url'),
    path('Attribute/<int:author_id>/getAuthorsAttr/', views.Attrs_by_author.as_view(), name='AttributeAuthor_url'),
]
