
from keras.models import load_model
import numpy as np
from keras.models import Model
from gensim.models import KeyedVectors
import re 
import tqdm

class Main:
    
    #Initialize with saved model and embeddings
    def __init__(self, path_model, path_embedding):
        self.model = load_model(path_model)
        self.word_vectors = KeyedVectors.load_word2vec_format(path_embedding, binary=True)
        
    #Helper function to create feature maps
    def get_feature_maps(self, layer_id, input_text):
        model_ = Model(inputs=[self.model.input], outputs=[self.model.layers[layer_id].output])
        return model_.predict(input_text)
    
    #Helper function to get embedding
    def embedd_text(self, x):
        final = []
        for i in x:
            sequence, count = np.zeros((100, 300), dtype=float), 0
            i = re.sub(r'[^\w\s]','',i)
            for word in i.split():
                if word in self.word_vectors.vocab:
                    if count<100: 
                        sequence[count] = self.word_vectors.get_vector(word)
                count += 1
            final.append(sequence)
        return final
        
    #Helper function to predict 
    def predict_text(self, x):
        final_list = []
        print("LSTM Prediction in progress.\n")
        for ind, i in tqdm.tqdm(enumerate(x)):
            temp_map = list(self.get_feature_maps(0, i.reshape(1,100,300))[0])
            final_list.append(temp_map)
        return final_list
    

    #Helper fucntion to combine DF to predictions
    def combine_text(self, df, prediction, label):
        new_cols = np.zeros((len(df),len(prediction[0])))
        for ind, i in enumerate(prediction):
            new_cols[ind,:] = i
        for i in range(len(prediction[0])):
            df[label+str(i+1)] = new_cols[:,i]
        return df