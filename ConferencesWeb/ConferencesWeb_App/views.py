from django.shortcuts import render, redirect
from datetime import date
from django.http import HttpResponse
import psycopg2
from ConferencesWeb_App.models import  Conference, Mm, Author, AuthUser
import random
from rest_framework.response import Response
from rest_framework.views import APIView
from ConferencesWeb_App.serializers import *
from rest_framework import status
from ConferencesWeb_App.minio import delete_pic, add_pic
from datetime import datetime, timedelta



conn = psycopg2.connect(dbname="conferences_web", host="localhost", user="postgres", password="1111", port="5432")

cursor = conn.cursor()

current_user_id = 1

def getActiveUser(): 
    return 1

def getDraftConferenceForUser(userId): #поиск черновой заявки под текущего пользователя
    Conf = None
    try:
        Conf = Conference.objects.get(creator=userId, status = 'draft')
    except Conference.DoesNotExist:
        Conf = Conference.objects.create(creator= AuthUser.objects.get(id = userId), status = 'draft', date_created = datetime.now())
    return Conf

class AuthorsList(APIView):
    model_class = Author
    serializer_class = AuthorSerializer

    def get(self, request): #список с фильтрацией
        search_author = ''
        if 'search_author' in request.GET:
            search_author = request.GET['search_author']
        authors = self.model_class.objects.filter(status='active', name__icontains=search_author).all()
        serializer = self.serializer_class(authors, many=True)

        draft_conference_id = getDraftConferenceForUser(getActiveUser()).conference_id
        draft_conference_authors_count = len(Mm.objects.filter(conference_id=draft_conference_id).all())

        return Response({
            'draft_conference_id': draft_conference_id,
            'draft_conference_authors_count': draft_conference_authors_count,
            'authors': serializer.data
        })
    
    def post(self, request):    #добавление без изображения
        serializer = self.serializer_class(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(request.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

class SingleAuthor(APIView):
    model_class = Author
    serializer_class = AuthorSerializer

    def get(self, request, id): #одна запись автор
        try:
            author = self.model_class.objects.get(author_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(author)
        return Response(serializer.data)

    def put(self, request, id): #изменение записи автор
        try:
            author = self.model_class.objects.get(author_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(author, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id): #удаление записи автор
        try:
            author = self.model_class.objects.get(author_id=id, status='active')
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        img_result = delete_pic(author)
        if 'error' in img_result.data:
            return img_result
        author.status = 'deleted'
        author.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AuthorAdding(APIView):    
    model_class = Mm
    serializer_class = MmSerializer

    def post(self, request, id):    #добавление автора в заявку
        try:
            author = Author.objects.get(author_id=id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        Conference = getDraftConferenceForUser(getActiveUser())
        Mm.objects.get_or_create(conference_id=Conference.conference_id, author_id=author.author_id, is_corresponding=False)
        return Response(status=status.HTTP_200_OK)


class AuthorImageUpload(APIView): 
    model_class = Author
    serializer_class = AuthorSerializer

    def post(self, request, id): #добавление изображения
        try:
            author = self.model_class.objects.get(author_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        img_result = add_pic(author, request.FILES.get('image'))
        if 'error' in img_result.data:
            return img_result
        return Response(status=status.HTTP_200_OK)

class ConferencesList(APIView):     
    model_class = Conference
    serializer_class = ConferenceSerializer

    def get(self, request):     #список конференций с фильтрацией
        filter_status = None
        min_date_formed = None
        max_date_formed = None

        if 'status' in request.GET:
            filter_status = request.GET['status']
        if 'min_date_formed' in request.GET:
            min_date_formed = request.GET['min_date_formed']
        if 'max_date_formed' in request.GET:
            max_date_formed = request.GET['max_date_formed']

        conferences = self.model_class.objects.filter(status__in=['formed', 'confirmed', 'rejected']).all()

        if filter_status != None:
            conferences = conferences.filter(status=filter_status)
        if min_date_formed != None and max_date_formed!=None:
            conferences = conferences.filter(date_formed__range=[min_date_formed, max_date_formed])

        if not conferences:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.serializer_class(conferences, many=True)
        return Response(serializer.data)

class SingleConference(APIView):    
    model_class = Conference
    serializer_class = SingleConfSerializer

    def get(self, request, id):     #одна конференция
        try:
            conference = self.model_class.objects.get(conference_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if conference:
            serializer = self.serializer_class(conference)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data)

    def put(self, request, id):     #изменение полей конференции
        try:
            conference = self.model_class.objects.get(conference_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(conference, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):  #удаление конференции
        try:
            conference = self.model_class.objects.get(conference_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        conference.status = 'deleted'
        conference.date_formed = datetime.now()
        conference.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ConferenceForming(APIView):
    model_class = Conference
    serializer_class = ConferenceSerializer

    def put(self, request, id): #сформировать создателем
        try:
            conference = self.model_class.objects.get(conference_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if conference.status != 'draft':
            return Response({'Error':'You can form only draft conferences'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not conference.conf_start_date:
            return Response({'Error': 'Required fields are not filled in'})
        
        conference.date_formed = datetime.now()
        conference.status = 'formed'
        conference.save()
        serializer = self.serializer_class(conference)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConferenceConfirming(APIView):
    model_class = Conference
    serializer_class = ConferenceSerializer

    def put(self, request, id): #завершить модератором
        try:
            conference = self.model_class.objects.get(conference_id=id, creator = getActiveUser())
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if conference.status != 'formed':
            return Response({'Error':'You can confirm only formed conferences'}, status=status.HTTP_400_BAD_REQUEST)
        
        conference.moderator = AuthUser.objects.get(id = getActiveUser())
        conference.date_ended = datetime.now()
        IsConfirmed = request.query_params.get('isConfirmed')
        print (IsConfirmed)
        if IsConfirmed == '1':
            conference.status = 'confirmed'
        else:
            conference.status = 'rejected'
        
        conference.conf_end_date = conference.conf_start_date + timedelta(hours=2)
        conference.members_count = Mm.objects.filter(conference_id=id).count()
        conference.save()
        serializer = self.serializer_class(conference)
        return Response(serializer.data, status=status.HTTP_200_OK)

class mm(APIView):
    model_class = Mm
    serializer_class = MmSerializer

    def delete(self, request, conf_id, author_id):  #удаление из заявки
        conference = Conference.objects.get(conference_id=conf_id, creator = getActiveUser())
        if conference.status in ['confirmed', 'rejected']:
            return Response({'Error':'You cant delete authors from moderated conferences'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mm = self.model_class.objects.get(conference_id=conf_id, author_id=author_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        mm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, conf_id, author_id): #изменение полей м-м
        conference = Conference.objects.get(conference_id=conf_id, creator = getActiveUser())
        if conference.status in ['confirmed', 'rejected']:
            return Response({'Error':'You cant modify authors in moderated conferences'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mm = self.model_class.objects.get(conference_id=conf_id, author_id=author_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        isCorr = request.query_params.get('is_corresponding')
        if isCorr not in ['0', '1']:
            return Response({'Error': 'Invalid value for is_corresponding'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(mm, data={'is_corresponding': isCorr}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistration(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer

    def post(self, request):    #регистрация пользователя
        if not request.data.get('username') or not request.data.get('password') or not request.data.get('email'):
            return Response({"error": "Registration information not provided"}, status=status.HTTP_400_BAD_REQUEST)
        if self.model_class.objects.filter(username=request.data.get('username')).exists():
            return Response({"error": "This username is taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = self.model_class.objects.create_user(username=request.data.get('username'), 
                                                    password=request.data.get('password'), 
                                                    email=request.data.get('email'),
                                                    is_superuser = request.data.get('is_superuser'),
                                                    first_name = request.data.get('first_name'),
                                                    last_name = request.data.get('last_name'),
                                                    is_staff = request.data.get('is_staff'),
                                                    is_active = request.data.get('is_active'),
                                                    date_joined = datetime.now())
        return Response(status=status.HTTP_201_CREATED)
       

class UserLK(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer

    def put(self, request):     #ЛК пользователя
        user = self.model_class.objects.get(id=getActiveUser())
        return Response(self.serializer(user).data)
        
class UserLogIn(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer

    def post(self, request):    #аутентификация пользователя
        if not request.data.get('username') or not request.data.get('password'):
            return Response({"error": "Authorization details not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.model_class.objects.get(username=request.data.get('username'))
        except self.model_class.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(request.data.get('password')):
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'authentification':'success'}, status=status.HTTP_200_OK)

class UserLogOut(APIView):
    model_class = get_user_model()
    serializer = AuthUserSerializer    

    def post(self, request):    #деавторизация пользователя
        return Response({'deauthorisation':'complete'})



