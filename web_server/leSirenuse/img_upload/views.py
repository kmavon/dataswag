from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import json
import os


@csrf_exempt
def img_upload(request):
    print('removing previous files')
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            os.remove(settings.MEDIA_ROOT + '\\' + filename)

    print('saving new files')
    fs = FileSystemStorage()
    for i, img in request.FILES.items():
        print(str(i) + ': ' + img.name)
        filename = fs.save(img.name, img)
    return HttpResponse('{"success": true}')


@csrf_exempt
def get_ranked_pics(request):
    # rank = recommender.rank(settings.MEDIA_URL, target=request.POST['target'])
    # until we actually have a recommender to produce the scores, we'll just
    # generate a dummy ranking
    rank = {}
    rank_list = []
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            rank_list.append({
                'pic_url': 'http://media.localhost:8000' + settings.MEDIA_URL + filename,
                'score': 94
                })
            print(filename + ': ' + str(rank_list[-1]['score']))
    rank['rank'] = rank_list
    return HttpResponse(json.dumps(rank))
