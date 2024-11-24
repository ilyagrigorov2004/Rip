from django.db import models
from rest_framework.relations import SlugRelatedField

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

class Conference(models.Model):
    conference_id = models.AutoField(primary_key=True)
    status = models.TextField()
    date_created = models.DateTimeField()
    creator = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, related_name='creator_conferences')
    date_formed = models.DateTimeField(blank=True, null=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    moderator = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, related_name='ModeratorConferences')
    conf_start_date = models.DateTimeField(blank=True, null=True)
    conf_end_date = models.DateTimeField(blank=True, null=True)
    members_count = models.IntegerField(blank=True, null=True)
    review_result = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conference'

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    description = models.TextField(unique=True)
    status = models.TextField()
    url = models.TextField(blank=True, null=True)
    department = models.TextField()
    birthdate = models.TextField()

    class Meta:
        managed = False
        db_table = 'author'

class Mm(models.Model):
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING, related_name='linked_authors')
    conference = models.ForeignKey(Conference, on_delete=models.DO_NOTHING, related_name='linked_conferences')
    is_corresponding = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mm'
        constraints = [
            models.UniqueConstraint(fields=['author_id', 'conference_id'], name='u_key')
        ]