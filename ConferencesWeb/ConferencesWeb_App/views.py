from django.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse
import psycopg2
from .models import  Conference, Mm, Author, AuthUser
import random

conn = psycopg2.connect(dbname="conferences_web", host="localhost", user="postgres", password="1111", port="5432")

cursor = conn.cursor()

current_user_id = 1


def getAuthorById(AuthorId):
    return Author.objects.get(author_id=AuthorId)

def getDraftByConferenceIdandUserId(ConfId, UserId):
    return Conference.objects.filter(conference_id = ConfId, creator_id=UserId, status='draft').first()

def getMMByConference(ConferenceId):
    return Mm.objects.filter(conference_id=ConferenceId).all()

def getConferenceByUserId(UserId):
    return Conference.objects.filter(creator_id=UserId, status='draft').first() 

def AuthorsController(request):
    AuthorsInConferenceCnt = 0
    CurConfId = -1

    CurConf = getConferenceByUserId(current_user_id)
    if CurConf!= None:
        CurConfId = CurConf.conference_id
        Authors_in_cur_conf = getMMByConference(CurConfId)
        AuthorsInConferenceCnt = len(Authors_in_cur_conf)
    search = ''
    if 'search_author' in request.GET:
        search = request.GET['search_author']
    found_authors = Author.objects.filter(name__icontains=search)

    return render(request, 'Authors.html', {'data' : {
        'Authors': found_authors,
        'ConferenceMembersCount' : AuthorsInConferenceCnt,
        'Conference_id' : CurConfId
    }})

def AuthorDescriptionController(request, id):

    Author = getAuthorById(id)    

    if Author == None:
        return redirect(AuthorsController)

    return render(request, 'SingleAuthor.html', {'data' : {
        'Author' : Author,
        'id': id
    }})

def ConferencesController(request, id):
    CurDraftConf = getDraftByConferenceIdandUserId(id, current_user_id)

    if CurDraftConf == None:
        return HttpResponse(status = 404)

    Author_in_con_list = getMMByConference(id)
    Authors = []

    for iAuthor in Author_in_con_list:
        author = getAuthorById(iAuthor.author_id)
        if author != None:
            Authors.append({
                'image' : author.url,
                'name' : author.name,
                'department' : author.department,
                'isCorresponding' : iAuthor.is_corresponding
            })

    if CurDraftConf.conf_start_date == None:
        CurDraftConf.conf_start_date = ''
    if CurDraftConf.conf_end_date == None:
        CurDraftConf.conf_end_date = ''
    
    CurDraftConf.members_count = len(Author_in_con_list)
    
    return render(request, 'Conferences.html', {'data' : {
        'id': id,
        'conf_start_date': CurDraftConf.conf_start_date,
        'conf_end_date' : CurDraftConf.conf_end_date,
        'members_count' : CurDraftConf.members_count,
        'conf_review_result' : CurDraftConf.review_result,
        'Authors': Authors
    }})

def AddAuthorController(request, id):
    Author = getAuthorById(id)
    if Author == None:
        return redirect(AuthorsController)
    
    curConf = getConferenceByUserId(current_user_id)
    if curConf == None:
        CurUser = AuthUser.objects.get(id=current_user_id)
        curConf = Conference.objects.create(creator_id = CurUser.id, status = 'draft', date_created = datetime.today(), review_result = random.randint(-2, 2))
    Mm.objects.get_or_create(conference_id=curConf.conference_id, author_id=Author.author_id, is_corresponding = False)

    return redirect(AuthorsController)

def DeleteConferenceController(request, id):
    if id!=None:
        cursor.execute('UPDATE conference SET status = %s WHERE conference_id = %s', ("deleted", id,))
    conn.commit()
    return redirect(AuthorsController)