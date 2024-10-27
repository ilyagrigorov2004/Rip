from django.shortcuts import render
from datetime import date


def ScientistsController(request):

    Conference_id = 3

    ConferenceMembersCount = 0
    for Conference in Conferences_list:
        if Conference['id'] == Conference_id:
            ConferenceMembersCount =  len(Conference['ItemIds'])

    search = ''
    if 'search_scientist' in request.GET:
        search = request.GET['search_scientist']

    Scientists_list_main = []

    for Scientist in Scientists_list:
        if search.lower() in Scientist['name'].lower():
            Scientists_list_main.append(Scientist)

    return render(request, 'Scientists.html', {'data' : {
        'Scientists': Scientists_list_main,
        'ConferenceMembersCount' : ConferenceMembersCount,
        'Conference_id' : Conference_id
    }})

def ConferencesController(request, id):

    Scientists_in_conf_list = []
    cur_conference = []
    for Conference in Conferences_list:
        if Conference['id'] == id:
            cur_conference = Conference
            for i in Conference['ItemIds']:
                for Scientist in Scientists_list:
                    if Scientist['id'] == i:
                        Scientists_in_conf_list.append(Scientist)
    return render(request, 'Conferences.html', {'data' : {
        'id': id,
        'cur_conference': cur_conference,
        'Scientists': Scientists_in_conf_list
    }})

def ScientistDescriptionController(request, id):
    return render(request, 'SingleScientist.html', {'data' : {
        'Scientist' : Scientists_list[id-1],
        'id': id
    }})

