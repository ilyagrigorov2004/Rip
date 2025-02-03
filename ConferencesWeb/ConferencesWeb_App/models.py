from django.db import models
from rest_framework.relations import SlugRelatedField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class Conference(models.Model):
    conference_id = models.AutoField(primary_key=True)
    status = models.TextField()
    date_created = models.DateTimeField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, related_name='creator_conferences')
    date_formed = models.DateTimeField(blank=True, null=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    moderator = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, related_name='ModeratorConferences')
    conf_start_date = models.DateTimeField(blank=True, null=True)
    conf_end_date = models.DateTimeField(blank=True, null=True)
    members_count = models.IntegerField(blank=True, null=True)
    review_result = models.IntegerField(blank=True, null=True)
    qr  = models.TextField(blank=True, null=True)

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

class Attribute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'attribute'


class AttributeAuthor(models.Model):
    id = models.AutoField(primary_key=True)
    attr_id = models.IntegerField()
    author_id = models.IntegerField()
    value = models.TextField(blank=True, null=True, default='')

    class Meta:
        managed = False
        db_table = 'attribute_author'
        unique_together = (('attr_id', 'author_id'),)
