from django.shortcuts import render
from datetime import date


Conferences_list = [
    {
        'id': 1,
        'theme': 'Необратимые процессы в природе и технике',
        'start_datetime':'',
        'end_datetime':'',
        'ItemIds':[1, 2, 3],
        'is': 2
    },
    {
        'id': 2,
        'theme': 'Физические интерпретации теории относительности',
        'start_datetime':'',
        'end_datetime':'',
        'ItemIds':[],
        'LeaderId': -1
    },
    {
        'id': 3,
        'theme': 'Применение квантовой физики в медицинских исследованиях',
        'start_datetime':'',
        'end_datetime':'',
        'ItemIds':[3, 4, 5, 1],
        'LeaderId': 4
    }
]

Authors_list = [
    {'image': 'http://localhost:9000/conferencesimgs/img1.png',
    'name': 'Иванов Иван Иванович',
    'description':'Макроэкономика, Экономическая политика, Региональное развитие, Международная экономика, Институциональная экономика, Фискальная политика, Инновационная экономика, Экономическое неравенство, Экологическая экономика, Экономика труда.',
    'department': 'ИБМ-1',
    'birthdate': '28.06.1987',
    'id': 1
    },
    {'image': 'http://localhost:9000/conferencesimgs/img2.png',
    'name': 'Смирнов Марат Григорьевич',
    'description':'Теория принятия решений, Методы оптимизации, Исследование операций, 	Численные методы, Теория формальных языков',
    'department': 'ФН-12',
    'birthdate': '15.09.1995',
    'id': 2
    },
    {'image': 'http://localhost:9000/conferencesimgs/img3.png',
    'name': 'Петров Алексей Ильич',
    'description':'Аэрокосмические системы, Высокоточные летательные аппараты, Ракетные и импульсные системы, Динамика и управление полетом ракет и космических аппаратов',
    'department': 'СМ-1',
    'birthdate': '10.12.1980',
    'id': 3
    },
    {'image':  'http://localhost:9000/conferencesimgs/img4.png',  
    'name': 'Павлов Павел Павлович',
    'description':'Диагностические комплексы, Электромагнитные аппараты, Неинвазивные компьютерные системы, Лазерный анализ крови, Медицинская физика, Биомедицинская оптика',
    'department': 'БМТ-1',
    'birthdate': '11.03.1996',
    'id': 4
    },
    {'image': 'http://localhost:9000/conferencesimgs/img5.png', 
    'name': 'Генадьев Николай Викторович',
    'description':'Высокочувствительные фищические измерения, физика экстремальных ситуаций, анализ и прогноз развития катастроф, природныу и техногенные процессы',
    'department': 'ФН-4',
    'birthdate': '13.04.1955',
    'id': 5
    },
    {'image': 'http://localhost:9000/conferencesimgs/img6.png', 
    'name': 'Гребнев Иннокентий Григорьевич',
    'description':'оптические, акустические и электродинамические методы исследования материалов и сред, Квантовая физика',
    'department': 'ФН-4',
    'birthdate': '08.11.1966',
    'id': 6
    }
]

def AuthorsController(request):

    Conference_id = 3

    ConferenceMembersCount = 0
    for Conference in Conferences_list:
        if Conference['id'] == Conference_id:
            ConferenceMembersCount =  len(Conference['ItemIds'])

    search = ''
    if 'search_author' in request.GET:
        search = request.GET['search_author']

    Authors_list_main = []

    for Author in Authors_list:
        if search.lower() in Author['name'].lower():
            Authors_list_main.append(Author)

    return render(request, 'Authors.html', {'data' : {
        'Authors': Authors_list_main,
        'ConferenceMembersCount' : ConferenceMembersCount,
        'Conference_id' : Conference_id
    }})

def ConferencesController(request, id):

    Authors_in_conf_list = []
    cur_conference = []
    for Conference in Conferences_list:
        if Conference['id'] == id:
            cur_conference = Conference
            for i in Conference['ItemIds']:
                for Author in Authors_list:
                    if Author['id'] == i:
                        Authors_in_conf_list.append(Author)
    return render(request, 'Conferences.html', {'data' : {
        'id': id,
        'cur_conference': cur_conference,
        'Authors': Authors_in_conf_list
    }})

def AuthorDescriptionController(request, id):
    return render(request, 'SingleAuthor.html', {'data' : {
        'Author' : Authors_list[id-1],
        'id': id
    }})

