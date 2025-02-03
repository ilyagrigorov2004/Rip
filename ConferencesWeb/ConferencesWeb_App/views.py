import psycopg2
from ConferencesWeb_App.models import  Conference, Mm, Author, Attribute, AttributeAuthor
from rest_framework.response import Response
from rest_framework.views import APIView
from ConferencesWeb_App.serializers import *
from rest_framework import status
from ConferencesWeb_App.minio import delete_pic, add_pic
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import permissions
import uuid
from .GetUserBySessionId import getUserBySessionId, session_storage
from django.contrib.auth.models import AnonymousUser
from .permissions import *
from .services.qr_generate import generate_conf_qr

conn = psycopg2.connect(dbname="conferences_web", host="localhost", user="postgres", password="1111", port="5432")

cursor = conn.cursor()

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            user = getUserBySessionId(self.request)
            if user == AnonymousUser():
                return Response({"detail": "Авторизация не пройдена."}, status=401)
            else:
                try:
                    self.check_permissions(self.request)
                except Exception as e:
                    return Response({"detail": "У Вас нет прав на выполнение этих действий"}, status=403)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

def getDraftConferenceForUser(request): #поиск черновой заявки под текущего пользователя
    Conf = None
    user = getUserBySessionId(request)
    if user == None:
        return None
    try:
        Conf = Conference.objects.get(creator=user.pk, status = 'draft')
    except Conference.DoesNotExist:
        Conf = Conference.objects.create(creator= get_user_model().objects.get(id = user.pk), status = 'draft', date_created = datetime.now())
    return Conf

class AuthorsList(APIView):
    model_class = Author
    serializer_class = AuthorSerializer

    @swagger_auto_schema(query_serializer=AuthorsListQuerySerializer, responses={200: AuthorsListResponseeSerializer})
    def get(self, request): #список с фильтрацией
        search_author = ''
        ActiveUser = getUserBySessionId(self.request)
        if 'search_author' in request.GET:
            search_author = request.GET['search_author']

        authors = self.model_class.objects.filter(name__icontains=search_author).all()
        if len(authors) == 0:
            authors = self.model_class.objects.filter(department__icontains=search_author).all()

        if(ActiveUser):        
            if not (ActiveUser.is_staff or ActiveUser.is_superuser):
                authors = authors.filter(status='active').all()

        serializer = self.serializer_class(authors, many=True)

        if ActiveUser!=AnonymousUser():
            draft_conference = ActiveUser.creator_conferences.filter(status='draft').first()
            if draft_conference:
                draft_conference_id = getDraftConferenceForUser(request).conference_id
                draft_conference_authors_count = len(Mm.objects.filter(conference_id=draft_conference_id).all())
            else:
                draft_conference_id = 0
                draft_conference_authors_count = 0
        else:
            draft_conference_id = 0
            draft_conference_authors_count = 0

        return Response({
            'draft_conference_id': draft_conference_id,
            'draft_conference_authors_count': draft_conference_authors_count,
            'authors': serializer.data
        })
    
    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAdmin,))
    def post(self, request):    #добавление без изображения
        serializer = self.serializer_class(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAdmin,))
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

    @method_permission_classes((IsAdmin,))
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

    @method_permission_classes((IsAuth,))
    def post(self, request, id):    #добавление автора в заявку
        try:
            author = Author.objects.get(author_id=id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        Conference = getDraftConferenceForUser(request)
        Mm.objects.get_or_create(conference_id=Conference.conference_id, author_id=author.author_id, is_corresponding=False)
        return Response(status=status.HTTP_200_OK)

class AuthorImageUpload(APIView): 
    model_class = Author
    serializer_class = AuthorSerializer

    @swagger_auto_schema(request_body=addPicSerializer, responses={200: AuthorSerializer})
    @method_permission_classes((IsAdmin,))
    def post(self, request, id): #добавление изображения
        try:
            author = self.model_class.objects.get(author_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        img_result = add_pic(author, request.FILES.get('image'))
        resp = self.serializer_class(author)
        if 'error' in img_result.data:
            return img_result
        return Response(resp.data, status=status.HTTP_200_OK)

class ConferencesList(APIView):     
    model_class = Conference
    serializer_class = ConferenceSerializer

    @swagger_auto_schema(query_serializer=ConfSearchSerializer)
    @method_permission_classes((IsAuth,))
    def get(self, request):     #список конференций с фильтрацией
        filter_status = None
        min_date_formed = None
        max_date_formed = None
        ActiveUser = getUserBySessionId(request)

        if 'status' in request.GET:
            filter_status = request.GET['status']
        if 'min_date_formed' in request.GET:
            min_date_formed = request.GET['min_date_formed']
        if 'max_date_formed' in request.GET:
            if request.GET['max_date_formed'] != '':
                max_date_formed = (datetime.strptime(request.GET['max_date_formed'], '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        conferences = self.model_class.objects.filter(status__in=['formed', 'confirmed', 'rejected']).all()

        if filter_status != '':
            conferences = conferences.filter(status=filter_status)
        if min_date_formed:
            conferences = conferences.filter(date_formed__gte=min_date_formed)
        if max_date_formed:
            conferences = conferences.filter(date_formed__lte=max_date_formed)

        if not (ActiveUser.is_staff or ActiveUser.is_superuser):
            conferences = conferences.filter(creator=ActiveUser)

        if not conferences:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.serializer_class(conferences, many=True)
        return Response(serializer.data)

class SingleConference(APIView):    
    model_class = Conference
    serializer_class = SingleConfSerializer

    @method_permission_classes((IsAuth,))
    def get(self, request, id):     #одна конференция
        ActiveUser = getUserBySessionId(request)
        try:
            if not (ActiveUser.is_staff or ActiveUser.is_superuser):
                conference = self.model_class.objects.get(conference_id=id, creator = ActiveUser)
            else:
                conference = self.model_class.objects.get(conference_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if conference:
            serializer = self.serializer_class(conference)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAuth,))
    def put(self, request, id):     #изменение полей конференции
        ActiveUser = getUserBySessionId(request)
        try:
            if not (ActiveUser.is_staff or ActiveUser.is_superuser):
                conference = self.model_class.objects.get(conference_id=id, creator = ActiveUser)
            else:
                conference = self.model_class.objects.get(conference_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if 'conf_start_date' in request.data and 'conf_end_date' in request.data and request.data['conf_start_date'] != '' and request.data['conf_end_date'] != '':
            conference.conf_start_date = datetime.strptime(request.data['conf_start_date'], '%Y-%m-%dT%H:%M')
            conference.conf_end_date = datetime.strptime(request.data['conf_end_date'], '%Y-%m-%dT%H:%M')
            if request.data['conf_start_date'] >= request.data['conf_end_date']:
                return Response({'Error': 'Дата начала должна быть меньше даты окончания'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data.pop('conf_start_date', None)
            request.data.pop('conf_end_date', None)

        if (ActiveUser.is_superuser or ActiveUser.is_staff) and 'review_result' in request.data :
            conference.review_result = request.data['review_result']

        serializer = self.serializer_class(conference, data=request.data, partial=True)
        conference.save()
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAuth,))
    def delete(self, request, id):  #удаление конференции
        ActiveUser = getUserBySessionId(request)
        try:
            if not (ActiveUser.is_staff or ActiveUser.is_superuser):
                conference = self.model_class.objects.get(conference_id=id, creator = ActiveUser)
            else:
                conference = self.model_class.objects.get(conference_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        conference.status = 'deleted'
        conference.date_formed = datetime.now()
        conference.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ConferenceForming(APIView):
    model_class = Conference
    serializer_class = ConferenceSerializer

    @swagger_auto_schema()
    @method_permission_classes((IsAuth,))
    def put(self, request, id): #сформировать создателем
        ActiveUser = getUserBySessionId(request)
        try:
            conference = self.model_class.objects.get(conference_id=id, creator = ActiveUser)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if conference.status != 'draft':
            return Response({'Error':'Можно изменять только черновые конференции'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not conference.conf_start_date:
            return Response({'Error': 'Заполните все поля'}, status=status.HTTP_400_BAD_REQUEST)
        
        conference.date_formed = datetime.now()
        conference.status = 'formed'
        conference.save()
        serializer = self.serializer_class(conference)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConferenceConfirming(APIView):
    model_class = Conference
    serializer_class = ConferenceSerializer

    @swagger_auto_schema(query_serializer=ConfirmSerializer)
    @method_permission_classes((IsManager,))
    def put(self, request, id): #завершить модератором
        try:
            conference = self.model_class.objects.get(conference_id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if conference.status != 'formed':
            return Response({'Error':'Подтверждать можно только сформированные конференции'}, status=status.HTTP_400_BAD_REQUEST)
        
        conference.moderator = get_user_model().objects.get(id = getUserBySessionId(request).id)
        conference.date_ended = datetime.now()
        IsConfirmed = request.GET['is_confirmed']
        if IsConfirmed:
            if IsConfirmed == '1':
                conference.status = 'confirmed'
            else:
                conference.status = 'rejected'

        qr_code_base64 = generate_conf_qr(conference)
        conference.qr = qr_code_base64
        
        conference.conf_end_date = conference.conf_start_date + timedelta(hours=2)
        conference.members_count = Mm.objects.filter(conference_id=id).count()
        conference.save()
        serializer = self.serializer_class(conference)
        return Response(serializer.data, status=status.HTTP_200_OK)

class mm(APIView):
    model_class = Mm
    serializer_class = MmSerializer

    @method_permission_classes((IsAuth,))
    def delete(self, request, conf_id, author_id):  #удаление из заявки
        ActiveUser = getUserBySessionId(request)
        conference = Conference.objects.get(conference_id=conf_id, creator = ActiveUser)
        if conference.status in ['confirmed', 'rejected']:
            return Response({'Error':'Только черновая конференция может быть удалена'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mm = self.model_class.objects.get(conference_id=conf_id, author_id=author_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        mm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(query_serializer=MMChangeSerializer, responses={200: 'Success'})
    @method_permission_classes((IsAuth,))
    def put(self, request, conf_id, author_id): #изменение полей м-м
        ActiveUser = getUserBySessionId(request)
        conference = Conference.objects.get(conference_id=conf_id, creator = ActiveUser)
        if conference.status in ['confirmed', 'rejected']:
            return Response({'Error':'Изменять авторов можно только в черновых конференциях'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mm = self.model_class.objects.get(conference_id=conf_id, author_id=author_id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        isCorr = request.query_params.get('is_corresponding')
        print(isCorr)
        if isCorr not in ['true', 'false']:
            return Response({'Error': 'Неверное значение'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(mm, data={'is_corresponding': isCorr}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistration(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        if not request.data.get('password') or not request.data.get('username'):
            return Response({"status": "Не указаны данные для регистрации"}, status=status.HTTP_400_BAD_REQUEST)

        if self.model_class.objects.filter(email=request.data.get('email')).exists() or self.model_class.objects.filter(username=request.data.get('username')).exists():
            return Response({"status": "Пользователь с такими данными уже существует"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.model_class.objects.create_user(
            username=request.data['username'],
            email=request.data['email'], 
            password=request.data['password'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
        )
        return Response({'status': 'Успех'}, status=status.HTTP_200_OK)
       

class UserLK(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=UserLKSerializer)
    def put(self, request):     #ЛК пользователя
        
        user = getUserBySessionId(request)
        if user!= AnonymousUser():
            serializer = self.serializer_class(user, data=request.data, partial=True)
        else: 
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            serializer.save()
            if (request.data.get('password')):
                user.set_password(request.data['password'])
                user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserLogIn(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):    #аутентификация пользователя
        if not request.data.get('username') or not request.data.get('password'):
            return Response({"error": "Заполните все поля авторизации"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None:
            random_key = uuid.uuid4().hex
            for key in session_storage.scan_iter():
                if session_storage.get(key).decode('utf-8') == user.email:
                    session_storage.delete(key)
            session_storage.set(random_key, user.email)
            response = Response(self.serializer_class(user).data)
            response.set_cookie('session_id', random_key)
            return response
        
        return Response({"error": "Неверный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)

class UserLogOut(APIView):
    model_class = get_user_model()
    serializer_class = UserSerializer    

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):    #деавторизация пользователя
        session_id = request.COOKIES.get('session_id')
        session_storage.delete(session_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class newAttribute(APIView):
    model_class = Attribute
    serializer_class = AttributeSerializer

    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsManager,))
    def post(self, request):    #добавление атрибута
        if(self.model_class.objects.filter(name=request.data['name']).exists()):
            return Response({'Error': 'Атрибут с таким именем уже существует'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class Attribute_by_id(APIView):
    model_class = Attribute
    serializer_class = AttributeSerializer

    @swagger_auto_schema()
    @method_permission_classes((IsManager,))
    def delete(self, request, id):
        try:
            attribute = self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        attribute.delete()
        AttributeAuthor.objects.filter(attr_id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class Attr_Author(APIView):
    model_class = AttributeAuthor
    serializer_class = AttributeAuthorSerializer

    @swagger_auto_schema(request_body=EditAttrValueSerializer)
    @method_permission_classes((IsManager,))
    def put(self, request, author_id, attr_id):
        if request.data['value'] == '':
            try: 
                self.model_class.objects.get(author_id=author_id, attr_id=attr_id).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except self.model_class.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)

        attribute = self.model_class.objects.get_or_create(author_id=author_id, attr_id=attr_id)[0]
        serializer = self.serializer_class(attribute, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class Attrs_by_author(APIView):
    model_class = AttributeAuthor
    serializer_class = AttributeAuthorSerializer
    
    @swagger_auto_schema(responses = {200: AttrInAuthorRespSerializer})
    def get(self, request, author_id):
        empty_attrs = Attribute.objects.all()

        resp = []
        for attr in empty_attrs:
            resp.append({
                'id': None, 
                'attr_id': attr.id, 
                'author_id': author_id, 
                'name': attr.name,
                'value': ''})  
        for item in resp:
            if AttributeAuthor.objects.filter(author_id=author_id, attr_id=item['attr_id']):
                item['value'] = AttributeAuthor.objects.get(author_id=author_id, attr_id=item['attr_id']).value
        serializer = AttrInAuthorRespSerializer(resp, many=True)
        return Response(serializer.data)
