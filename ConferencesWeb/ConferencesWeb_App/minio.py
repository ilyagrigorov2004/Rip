from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *
import uuid

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('conferencesimgs', image_name, file_object, file_object.size)
        return f"http://localhost:9000/conferencesimgs/{image_name}"
    except Exception as e:
        return {"error": str(e)}
    
def process_file_delete(client, image_name):
    try:
        client.remove_object('conferencesimgs', image_name)
        return {'status':'success'}
    except Exception as e:
        return {'ERROR': str(e)}

def add_pic(author, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    random_key = uuid.uuid4().hex[:8]
    img_obj_name = f"{random_key}.jpg"

    if pic == None:
        return Response({"error": "No image."})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    delete_pic(author)
    author.url = result
    author.save()

    return Response({"message": "success"})

def delete_pic(author):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    pic_url = author.url
    author.url = None
    author.save()
    if pic_url:
        pic_url = '/'.join(pic_url.split('/')[4:])

    result = process_file_delete(client, pic_url)
    if 'error' in result:
        return Response(result)

    return Response({"message": "success"})