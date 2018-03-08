from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

@csrf_exempt
def img_upload(request):
    fs = FileSystemStorage()
    for i, img in request.FILES.items():
        print(str(i) + ': ' + img.name)
        filename = fs.save(img.name, img)
    return HttpResponse('{"success": true}')
