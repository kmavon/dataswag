
from keras.models import load_model
import numpy as np
from keras.models import Model
import tqdm

class Main:
    
    #Initialize with saved model and embeddings
    def __init__(self, path_model):
        self.model = load_model(path_model)
        
    #Helper function to create feature maps
    def get_feature_maps(self, layer_id, input_text):
        model_ = Model(inputs=[self.model.input], outputs=[self.model.layers[layer_id].output])
        return model_.predict(input_text)
        
    #Helper function to predict 
    def predict_image(self, x):
        final_list = []
        print("CNN Prediction in progress.\n")
        for ind, i in tqdm.tqdm(enumerate(x)):
            temp_map = list(self.get_feature_maps(9, i.reshape(1,64,64,3))[0])
            final_list.append(temp_map)
        return final_list
    

    #Helper fucntion to combine DF to predictions
    def combine_image(self, df, prediction, label):
        new_cols = np.zeros((len(df),len(prediction[0])))
        for ind, i in enumerate(prediction):
            new_cols[ind,:] = i
        for i in range(len(prediction[0])):
            df[label+str(i+1)] = new_cols[:,i]
        return df