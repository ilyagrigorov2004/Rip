from django.db import models

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
    creator = models.IntegerField(blank=True, null=True)
    date_formed = models.DateTimeField(blank=True, null=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    moderator = models.IntegerField(blank=True, null=True)
    conf_start_date = models.DateTimeField(blank=True, null=True)
    conf_end_date = models.DateTimeField(blank=True, null=True)
    members_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conference'


class Mm(models.Model):
    author_id = models.IntegerField()
    conference_id = models.IntegerField()
    leader = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mm'
        constraints = [
            models.UniqueConstraint(fields=['author_id', 'conference_id'], name='u_key')
        ]


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    description = models.TextField(unique=True)
    status = models.TextField()
    url = models.TextField(blank=True, null=True)
    department = models.TextField()
    birthdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'author'