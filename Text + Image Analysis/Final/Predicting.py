
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
        self.companies = {'athenaprocopiou': {'Prob_0': 0.004918032786880027, 'Prob_2': 0.9377051759688008, 'Prob_1': 0.040983348621368404, 'Prob_3': 0.01639344262295082}, 'daftcollectionofficial': {'Prob_0': 0.013245028652267732, 'Prob_2': 0.9105954903998748, 'Prob_1': 0.07615948094785772, 'Prob_3': 3.122015335038964e-107}, 'dodobaror': {'Prob_0': 0.0014554418860555601, 'Prob_2': 0.9810771470160117, 'Prob_1': 0.01746741109793279, 'Prob_3': 3.6167143590989286e-105}, 'heidikleinswim': {'Prob_0': 0.006674342236691975, 'Prob_2': 0.92651374018904, 'Prob_1': 0.06605776976129675, 'Prob_3': 0.0007541478129713424}, 'lisamariefernandez': {'Prob_0': 0.004550625921246749, 'Prob_2': 0.9510389898093446, 'Prob_1': 0.043272727843172015, 'Prob_3': 0.0011376564262365173}, 'loupcharmant': {'Prob_0': 0.025824962359344814, 'Prob_2': 0.9483500733425246, 'Prob_1': 0.017216642920799198, 'Prob_3': 0.00860832137733142}, 'miguelinagambaccini': {'Prob_0': 0.003883495145576984, 'Prob_2': 0.9611461770486399, 'Prob_1': 0.03302858023296752, 'Prob_3': 0.001941747572815534}, 'muzungusisters': {'Prob_0': 0.0036231884057971015, 'Prob_2': 0.9053762954279078, 'Prob_1': 0.0819425451518024, 'Prob_3': 0.009057971014492754}, 'zeusndione': {'Prob_0': 0.006999166615584516, 'Prob_2': 0.958005249343832, 'Prob_1': 0.030621130847232603, 'Prob_3': 0.004374453193350831}, 'zimmermann': {'Prob_0': 0.01904761904761905, 'Prob_2': 0.9555555555555556, 'Prob_1': 0.015873015873015886, 'Prob_3': 0.009523809523809525}}
       
    #Helper Function to get images from train path
    def get_target_posts(self):
        self.target_posts = []
        for j in glob.glob(self.target_path + '/*.jpg'):
            temp_dict = {}
            file_name = j.replace(self.target_path,'')[1:]
            try:
                img = image.load_img(j, target_size=(64, 64))
            except OSError:
                continue
            if self.captions_flag:
                try:
                    with open(j[:-4]+'.txt', encoding="utf-8") as f:
                        content = f.readlines()
                        caption = ' '.join([x.strip() for x in content])
                except FileNotFoundError:
                    continue
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
    def get_cluster_presence(self, df, extra_cols, model):

        #Filter Mean and Variance as per Text Input
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
    
    #Helper function to generate distance dictionary
    def get_dist2comp(self, df, extra_cols):
        
        #Filter Data
        data = df.copy(deep=True)
        
        #Delete reference columns
        for i in extra_cols:
            del data[i]             
        
        #Calculate distance to each cluster
        final = np.zeros((len(df), len(self.companies)))
        pred = []
        for i in range(0,len(df)):
            temp_dist = []
            for j in range(0, len(self.companies)):
                temp_company, temp_vector = list(self.companies.items())[j][0], list(self.companies.items())[j][1]
                temp_vector = np.array([temp_vector['Prob_0'],temp_vector['Prob_1'],temp_vector['Prob_2'],temp_vector['Prob_3']])
                dist_vec = np.linalg.norm(data.iloc[i,:].reshape(1,-1)-temp_vector.reshape(1,-1))
                temp_dist.append(dist_vec)
            final[i,:] = temp_dist
            pred.append(list(self.companies.items())[np.argmin(temp_dist)][0])
        columns = [list(self.companies.items())[k][0] for k in range(len(self.companies))]
        df_final = pd.DataFrame(final, columns=columns) 
        df_final['Prediction'] = pred
        df_final['File'] = df['File']
        return df_final