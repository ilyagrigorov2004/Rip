from ConferencesWeb_App.models import AuthUser, Conference, Mm, Author
from rest_framework import serializers
from django.contrib.auth import get_user_model


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['author_id', 'name', 'description', 'status', 'url', 'department', 'birthdate']

class ConferenceSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = Conference
        fields = ['conference_id', 'status', 'date_created', 'creator', 'date_formed', 'date_ended', 'moderator', 'conf_start_date', 'conf_end_date', 'members_count', 'review_result']

class MmSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField()    
    conference_id = serializers.IntegerField()    
    class Meta:
        model = Mm
        fields = ['author_id', 'conference_id', 'is_corresponding']

class MMwithAuthorSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Mm
        fields = ['author', 'is_corresponding']

class SingleConfSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    authors = MMwithAuthorSerializer(many=True, read_only=True, source='linked_conferences')

    class Meta:
        model = Conference
        fields = ['conference_id', 'status', 'date_created', 'creator', 'date_formed', 'date_ended', 'moderator', 'conf_start_date', 'conf_end_date', 'members_count', 'review_result', 'authors']
