from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import json

@csrf_exempt
def img_upload(request):
    fs = FileSystemStorage()
    for i, img in request.FILES.items():
        print(str(i) + ': ' + img.name)
        filename = fs.save(img.name, img)
    return HttpResponse('{"success": true}')

@csrf_exempt
def get_ranked_pics(request):
    # rank = recommender.rank(settings.MEDIA_URL)
    rank = {}
    rank_list = []
    for i in range(1, 11):
        rank_list.append({
            'pic_url': settings.MEDIA_URL + str(i) + '.jpg',
            'score': 100/i
            })
    rank['rank'] = rank_list
    print(rank)
    return HttpResponse(json.dumps(rank))
