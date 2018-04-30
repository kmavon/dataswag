
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
from keras.preprocessing import image

class Main:
    
    #Initialization
    def __init__(self, user_path, train_path, save_path):
        self.train_path = train_path
        self.save_path = save_path
        self.user_list_path = user_path
        
    #helper function to get User List   
    def get_user_list(self):
        with open(self.user_list_path, encoding="ISO-8859-1") as f:
            content = f.readlines()
        user_list = [x.strip() for x in content] 
        print("No# of Users Listed :",len(user_list))
        return user_list
        
    #Helper Function to get images from train path
    def get_train_posts(self, user_list, limit):
        list_users = user_list
        self.train_posts = []
        for i in list_users:
            count = 0
            temp_path = self.train_path + i
            for j in glob.glob(temp_path + '/*.jpg'):
                temp_dict = {}
                file_name = j.replace(temp_path,'')[1:]
                img = image.load_img(j, target_size=(64, 64))
                try:
                    with open(j[:-4]+'.txt', encoding="utf-8") as f:
                        content = f.readlines()
                        caption = ' '.join([x.strip() for x in content])
                except FileNotFoundError :
                    continue
                temp_dict['File'] = j.split('/')[-1]
                temp_dict['User'] = i
                temp_dict['Image'] = np.array(img)
                temp_dict['Caption'] = caption
                self.train_posts.append(temp_dict)
                count +=1
                if count==limit:
                    break
        print("Number of posts loaded:", len(self.train_posts))
        return pd.DataFrame(self.train_posts)
    
    #Helper function to cluster post features using GMM
    def fit_posts(self, df, k, extra_cols, rand_state):
        data = df.copy(deep=True)
        
        #Delete reference columns
        for i in extra_cols:
            del data[i]

        #Implement Gaussian Mixture Model Algortihm 
        model = GaussianMixture(n_components=k, random_state=9001)

        #Fit Model and Predict
        model.fit(data)
        y_pred = model.predict_proba(data)

        #Add prediction to dataframe and return 
        for i in range(0,k+1):
            if i==k:
                label = "Prediction"
                df[label] = model.predict(data)
                break
            label = "Prob_" + str(i)
            df[label] = y_pred[:,i]
        return df, model
    
    #Helper function to obtain percentage of presence of user in each post cluster
    def get_cluster_presence(self, df, k):
        cluster_presence = []
        for i in list(df['User'].unique()):
            user_dict = {}
            temp_df = df[df['User']==i]
            post_count  =  len(temp_df)
            user_dict['User'] = i
            for j in range(0, k):
                user_dict["Cluster_"+str(j)] = sum(temp_df['Prob_'+str(j)])/post_count
            cluster_presence.append(user_dict)
        df_presence = pd.DataFrame(cluster_presence)
        df_presence = df_presence.fillna(0)
        return df_presence
    
    #Helper function to cluster user post distribution using KMeans
    def fit_users(self, df, k, extra_cols, rand_state):
        data = df.copy(deep=True)
        
        #Delete reference columns
        for i in extra_cols:
            del data[i]

        #Implement Gaussian Mixture Model Algortihm 
        model = GaussianMixture(n_components=k, random_state=9001)

        #Fit Model and Predict
        model.fit(data)
        y_pred = model.predict_proba(data)

        #Add prediction to dataframe and return 
        for i in range(0,k+1):
            if i==k:
                label = "Prediction"
                df[label] = model.predict(data)
                break
            label = "Prob_" + str(i)
            df[label] = y_pred[:,i]
        return df, model
    
    #Helper function to create folders for Image Clustering
    def save_clusters(self, df, label):
        path = self.save_path + label + "/"
        count = 0
        for i in list(df['File'].unique()):
            temp_row = df[df["File"]==i]
            try:
                name, pred_folder = i, str(temp_row['Prediction'].values[0])
            except IndexError:
                continue
            temp_path = path + "Cluster" + pred_folder + "/"
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            io.imsave(temp_path+name, temp_row['Image'].values[0])
            count += 1
        print(str(count)+" Images Saved.")
    
    #Helper function to save model 
    def save_model(self, model, path):
        joblib.dump(model, path) 
        print("Model Saved.")