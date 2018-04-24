from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import json
import os
#import kmrec
import pandas as pd
import numpy as np
import random

# Initialize recommender object once, so that the plk model is imported just
# on server startup

# recommender = kmrec()

@csrf_exempt
def img_upload(request):
    print('removing previous files')
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            os.remove(settings.MEDIA_ROOT + '/' + filename)

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
                #'pic_url': 'http://media.localhost:8000' + settings.MEDIA_URL + filename,
                'pic_url': filename,
                'score': 94
                })
            print(filename + ': ' + str(rank_list[-1]['score']))
    rank['rank'] = rank_list
    return HttpResponse(json.dumps(rank))


@csrf_exempt
def get_scored_pics(request):
    # scores = kmrec().getscores()
    # scores_json = {}
    # communities = np.unique(scores['community'].as_array())
    # for community in communities:
    #     community_scores = scores.sort(columns="KL_score")[["picture_uploaded", "KL_score"]].head(5)
    #     for index, row in community_scores.iterrows():
    #         scores_json[community] = community_scores.to_dict("records")
    # clusters = ["cluster0", "cluster1", "cluster2", "cluster3", "cluster4", "cluster5"]
    # scores_json = {"scores": []}
    # for cluster in clusters:
    #     score_list = []
    #     for root, dirs, files in os.walk(settings.MEDIA_ROOT):
    #         for filename in files:
    #             score_list.append({"pic_url": filename, "score": random.uniform(1, 100)})
    #     scores_json["scores"].append({"name": cluster, "scores": score_list})
    scores_json = {}
    score_list = []
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            score_list.append({"pic_url": filename, "community": "cluster" + str(random.randint(0, 5))})
            scores_json["scores"] = score_list
    return HttpResponse(json.dumps(scores_json))
