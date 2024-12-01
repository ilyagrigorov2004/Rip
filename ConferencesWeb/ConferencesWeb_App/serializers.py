from ConferencesWeb_App.models import Conference, Mm, Author
from rest_framework import serializers
from django.contrib.auth import get_user_model
from collections import OrderedDict

class AuthUserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'is_staff', 'is_superuser']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['author_id', 'name', 'description', 'status', 'url', 'department', 'birthdate']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

class ConferenceSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = Conference
        fields = ['conference_id', 'status', 'date_created', 'creator', 'date_formed', 'date_ended', 'moderator', 'conf_start_date', 'conf_end_date', 'members_count', 'review_result']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

class MmSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField()    
    conference_id = serializers.IntegerField()    
    class Meta:
        model = Mm
        fields = ['author_id', 'conference_id', 'is_corresponding']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

class MMwithAuthorSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Mm
        fields = ['author', 'is_corresponding']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

class SingleConfSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    authors = MMwithAuthorSerializer(many=True, read_only=True, source='linked_conferences')

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

    class Meta:
        model = Conference
        fields = ['conference_id', 'status', 'date_created', 'creator', 'date_formed', 'date_ended', 'moderator', 'conf_start_date', 'conf_end_date', 'members_count', 'review_result', 'authors']
