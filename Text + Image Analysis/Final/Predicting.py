
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
from scipy import linalg
from scipy.special import logsumexp
from keras.preprocessing import image

class Main:
    
    #Initialization
    def __init__(self, target_path, flag):
        self.target_path = target_path
        self.captions_flag = flag
        
    #Helper Function to get images from train path
    def get_target_posts(self):
        self.target_posts = []
        for j in glob.glob(self.target_path + '/*.jpg'):
            temp_dict = {}
            file_name = j.replace(self.target_path,'')[1:]
            img = image.load_img(j, target_size=(64, 64))
            if self.captions_flag:
                with open(j[:-4]+'.txt', encoding="utf-8") as f:
                    content = f.readlines()
                    caption = ' '.join([x.strip() for x in content])
                temp_dict['Caption'] = caption    
            temp_dict['File'] = j.split('/')[-1]
            temp_dict['Image'] = np.array(img)
            self.target_posts.append(temp_dict)
        print("Number of posts loaded:", len(self.target_posts))
        return pd.DataFrame(self.target_posts)
    
    
    #Helper function to load saved model
    def load_model(self, path):
        model = joblib.load(path)
        print ("Model loaded.")
        return model
    
    #Helper function to get Log probability for full covariance matrices
    def lmnd_diag_full(self, X, means, covars, min_covar=1.e-7):
        n_samples, n_dim = X.shape
        nmix = len(means)
        log_prob = np.empty((n_samples, nmix))
        for c, (mu, cv) in enumerate(zip(means, covars)):
            try:
                cv_chol = linalg.cholesky(cv, lower=True)
            except linalg.LinAlgError:
                try:
                    cv_chol = linalg.cholesky(cv + min_covar * np.eye(n_dim), lower=True)
                except linalg.LinAlgError:
                    raise ValueError("'covars' must be symmetric, ""positive-definite")
            cv_log_det = 2 * np.sum(np.log(np.diagonal(cv_chol)))
            cv_sol = linalg.solve_triangular(cv_chol, (X - mu).T, lower=True).T
            log_prob[:, c] = - .5 * (np.sum(cv_sol ** 2, axis=1) +n_dim * np.log(2 * np.pi) + cv_log_det)
        return log_prob
    

    #Helper function to generate distance dictionary
    def get_cluster_presence(self, df, extra_cols, model, image_left=True):

        #Filter Mean and Variance as per Text Input
        if image_left:
            self.means = model.means_ if self.captions_flag else model.means_[:,:64] 
            self.covariances = model.covariances_ if self.captions_flag else model.covariances_[:,:64,:64]
        else:
            self.means = model.means_ if self.captions_flag else model.means_[:,64:]
            self.covariances = model.covariances_ if self.captions_flag else model.covariances_[:,64:,64:] 
        self.weights = model.weights_
        
        #Filter Data and save file names
        data = df.copy(deep=True)
        final = np.zeros((len(df),len(self.means)+1))
        
        #Delete reference columns
        for i in extra_cols:
            del data[i]
        
        #Calculate Probabilities of Presence
        for i in range(len(data)):
            current = data.iloc[i,:].values.reshape(1,-1)
            lpr = self.lmnd_diag_full(current, self.means, self.covariances) + np.log(self.weights)
            logprob = logsumexp(lpr, axis=1)
            responsibilities = np.exp(lpr - logprob[:, np.newaxis])
            final[i,:] = np.append(responsibilities[0],np.argmax(responsibilities[0]))
        
        #Create Dataframe
        colnames = ['Prob_'+str(i) for i in range(len(self.means))] + ['Prediction']
        df_final = pd.DataFrame(final, columns=colnames) 
        df_final['File'] = df['File']
        return df_final
                       
    #Helper function to generate distance dictionary
    def get_result(self, df, extra_cols, model):
        
        #Filter Data
        data = df.copy(deep=True)
        
        #Delete reference columns
        for i in extra_cols:
            del data[i]             
        
        #Calculate distance to each cluster
        final = np.zeros((len(df),len(model.means_)+1))
        for i in range(0,len(df)):
            temp_dist = []
            for j in range(0, len(model.means_)):
                dist_vec = np.linalg.norm(data.iloc[i,:].reshape(1,-1)-model.means_[j].reshape(1,-1))
                temp_dist.append(dist_vec)
            final[i,:] = temp_dist + [np.argmin(temp_dist)]
            columns = ['Dist_'+str(i) for i in range(len(model.means_))]+['Prediction']
            df_final = pd.DataFrame(final, columns=columns) 
            df_final['File'] = df['File']
        return df_final