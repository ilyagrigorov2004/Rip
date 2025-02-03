from ConferencesWeb_App.models import Conference, Mm, Author, Attribute, AttributeAuthor
from rest_framework import serializers
from django.contrib.auth import get_user_model
from collections import OrderedDict

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = get_user_model()
        fields = ['email', 'is_staff', 'is_superuser', 'username', 'first_name', 'last_name', 'password']

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
        fields = ['conference_id', 'status', 'date_created', 'creator', 'date_formed', 'date_ended', 'moderator', 'conf_start_date', 'conf_end_date', 'members_count', 'review_result', 'qr']

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

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

class AttributeAuthorSerializer(serializers.ModelSerializer):
    attr_id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    value = serializers.CharField(required=False)

    class Meta:
        model = AttributeAuthor
        fields = ['id', 'attr_id', 'author_id', 'value']

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields 

class AuthorsListQuerySerializer(serializers.Serializer):
    search_author = serializers.CharField(required=False)

class AuthorsListResponseeSerializer(serializers.Serializer):
    authors = AuthorSerializer(many=True)
    draft_conference_id = serializers.IntegerField()
    draft_conference_authors_count = serializers.IntegerField()

class UserLKSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

class MMChangeSerializer(serializers.Serializer):
    is_corresponding = serializers.BooleanField(required=False)

class ConfSearchSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    min_date_formed = serializers.DateTimeField(required=False)
    max_date_formed = serializers.DateTimeField(required=False)

class addPicSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)

class ConfirmSerializer(serializers.Serializer):
    is_сonfirmed = serializers.IntegerField(required=False)

class EditAttrValueSerializer(serializers.Serializer):
    value = serializers.CharField(required=False)

class AttrInAuthorRespSerializer(serializers.Serializer):
    attr_id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    name = serializers.CharField()
    value = serializers.CharField(required=False)