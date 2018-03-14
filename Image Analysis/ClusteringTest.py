
import skimage
import os
import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib
import matplotlib.pyplot as plt
from skimage import data
from skimage import io
import glob
from skimage.viewer import ImageViewer
import cv2
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.externals import joblib

class Ranking:
    
    #Initialization
    def __init__(self, target_path):
        self.target_path = target_path

    #Helper Function to get images from target path 
    def get_images_target(self):
        #Get all Images of Users in the List
        self.target_imgs = {}
        for j in glob.glob(self.target_path + '/*.jpg'):
            file_name = j.replace(self.target_path,'')[:]
            img = io.imread(j)
            self.target_imgs[("Input/Target",file_name)] = img
        print("Number of images loaded:", len(self.target_imgs))
    
    #Helper function to load saved model
    def load_model(self, path):
        model = joblib.load(path)
        print ("Model loaded.")
        return model

    #Helper function to convert image to d-dimension vector for each image and 
    #return dataframe of all images
    def convert_to_features(self, columns):
        features = []
        for i in self.target_imgs.items():
            r_mean, r_std, r_med = np.mean(i[1][:,:,0].ravel()), np.std(i[1][:,:,0].ravel()), np.median(i[1][:,:,0].ravel())
            g_mean, g_std, g_med  = np.mean(i[1][:,:,1].ravel()), np.std(i[1][:,:,1].ravel()), np.median(i[1][:,:,1].ravel())
            b_mean, b_std, b_med  = np.mean(i[1][:,:,2].ravel()), np.std(i[1][:,:,2].ravel()), np.median(i[1][:,:,2].ravel())
            canny = np.mean(np.ravel(cv2.Canny(cv2.cvtColor(i[1], cv2.COLOR_BGR2HSV),100,200,L2gradient = True)))
            try:
                orb = cv2.ORB_create(100)
                kp = orb.detect(i[1],None)
                kp, des = orb.compute(i[1], kp)
                orb_centers = list(KMeans(1).fit([i.pt for i in kp]).cluster_centers_)
                orbx1, orby1 = orb_centers[0][0]*255/np.shape(i[1])[0], orb_centers[0][1]*255/np.shape(i[1])[1]
            except ValueError:
                continue
            features.append(np.array([i[0][0],i[0][1], r_mean, r_std, r_med, g_mean, g_std, g_med, b_mean, b_std, b_med, canny, orbx1, orby1]))
        df = pd.DataFrame(features, columns = columns)
        return df

    #Helper function to make prediction for target images using image model
    def predict(self, df, model, k, cluster_names, extra_cols):
        data = df.copy(deep=True)
        
        #Delete reference columns
        for i in extra_cols:
            del data[i]
            
        #Make Prediction
        y_pred = model.predict_proba(data)
        
        #Add prediction to dataframe and return 
        for i in range(0,k+1):
            if i==k:
                label = "Prediction"
                df[label] = model.predict(data)
                break
            label = cluster_names[i] + " (" + str(i) + ")"
            df[label] = y_pred[:,i]
        return df
    
    #Helper function to generate distance dictionary
    def get_result(self, df, k, model):
        final_dict = {}
        for i in range(0,len(df)):
            temp_file = df.iloc[i,1]
            temp_dist = []
            for j in range(0, k):
                temp_dist.append(np.linalg.norm(df.iloc[i,14:14+k].astype(float)-model.cluster_centers_[j]))
            final_dict[temp_file] = temp_dist
        return final_dict