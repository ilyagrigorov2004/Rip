import segno
import base64
from io import BytesIO
from ConferencesWeb_App.models import Mm

def statustranslate(status):
    if status == 'draft':
        return 'Черновик'
    elif status == 'formed':
        return 'Сформирована'
    elif status == 'confirmed':
        return 'Подтверждена'
    elif status == 'rejected':
        return 'Отменена'
    elif status == 'deleted':
        return 'Удалена'
    else:
        return 'Неизвестный статус'

def generate_conf_qr(conference):
    # Формируем информацию для QR-кода
    info = f"Конференция №{conference.conference_id}\n\n"
    info += "Статус: " + statustranslate(conference.status) + "\n\n"
    if(conference.status == 'confirmed' or conference.status == 'rejected'):
        info += "Результат рецензирования: " + str(conference.review_result) + "\n"

    # Добавляем информацию об авторах
    info += "Авторы:\n"
    authors = Mm.objects.filter(conference=conference)

    for author in authors:
        if(author.is_corresponding == True): 
            info += f" - Ведуший "
        info += f"- {author.author.name}\n"
        info += f"\tКафедра {author.author.department}\n"

    info += "Начало конференции: " + str(conference.conf_start_date) + "\n"
    info += "Конец конференции: " + str(conference.conf_end_date) + "\n"

    info += "\nДата создания: " + str(conference.date_created) + "\n"
    info += "Дата формирования: " + str(conference.date_formed) + "\n"
    info += "Дата модерации: " + str(conference.date_ended) + "\n"

    # Генерация QR-кода
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    # Конвертация изображения в base64
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return qr_image_base64