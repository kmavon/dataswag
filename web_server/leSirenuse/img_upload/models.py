from django.db import models

class ImageModel(models.Model):
    model_pic = models.ImageField(upload_to = 'pics_to_rank/', default = 'pics_to_rank/none.jpg')
