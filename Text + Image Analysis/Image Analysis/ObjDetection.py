
#Import libraries
import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import coco
import utils
import model as modellib
import visualize
from collections import Counter

class InferenceConfig(coco.CocoConfig):
    #Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

class mask_rcnn:
    
    def __init__(self, model_path):
        print(model_path)
        #Root directory of the project
        self.ROOT_DIR = model_path
        
        #Directory to save logs and trained model
        self.MODEL_DIR = os.path.join(self.ROOT_DIR, "logs")
        
        #Local path to trained weights file
        self.COCO_MODEL_PATH = os.path.join(self.ROOT_DIR, "mask_rcnn_coco.h5")
        
        #Set-up configuration
        self.config = InferenceConfig() 
        
        #Create model object in inference mode.
        self.model = modellib.MaskRCNN(mode="inference", model_dir=self.MODEL_DIR, config=self.config)

        #Load weights trained on MS-COCO
        self.model.load_weights(self.COCO_MODEL_PATH, by_name=True)
    
        #Model detection classes
        self.class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']
        
    #Detect objects in the image
    def detect(self, img):
        #Run detection
        self.image = img
        self.results = self.model.detect([self.image], verbose=1)

    #Visualize results
    def get_result(self):
        #Visualize results
        r = self.results[0]
        visualize.display_instances(self.image, r['rois'], r['masks'], r['class_ids'], 
                            self.class_names, r['scores'])
    #Get Counts Dictionary
    def get_counts(self):
        self.count_dict = {}
        r = self.results[0]
        counts = Counter(r['class_ids'])
        for ind, i in enumerate(self.class_names):
            self.count_dict [i] = counts[ind]
        return (self.count_dict)
   