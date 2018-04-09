
import glob
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import pickle
from tqdm import tqdm
import pandas as pd
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import LSTM, Embedding, TimeDistributed, Dense, RepeatVector, Merge, Activation, Flatten
from keras.optimizers import Adam, RMSprop
from keras.layers.wrappers import Bidirectional
from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
import nltk
from keras.models import Model

def split_data(l):
    temp = []
    for i in img:
        if i[len(images):] in l:
            temp.append(i)
    return temp

def preprocess_input(x):
    x /= 255.
    x -= 0.5
    x *= 2.
    return x

def preprocess(img):
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x

def encode(image, model_new):
    image = preprocess(image)
    temp_enc = model_new.predict(image)
    temp_enc = np.reshape(temp_enc, temp_enc.shape[1])
    return temp_enc

def predict_captions(image, final_model, word2idx, idx2word, max_len):
    start_word = ["<start>"]
    while True:
        par_caps = [word2idx[i] for i in start_word]
        par_caps = sequence.pad_sequences([par_caps], maxlen=max_len, padding='post')
        preds = final_model.predict([np.array([image]), np.array(par_caps)])
        word_pred = idx2word[np.argmax(preds[0])]
        start_word.append(word_pred)
        
        if word_pred == "<end>" or len(start_word) > max_len:
            break
    return ' '.join(start_word[1:-1])


def beam_search_predictions(image, beam_index, final_model, word2idx, idx2word, max_len):
    start = [word2idx["<start>"]]
    start_word = [[start, 0.0]]
    while len(start_word[0][0]) < max_len:
        temp = []
        for s in start_word:
            par_caps = sequence.pad_sequences([s[0]], maxlen=max_len, padding='post')
            preds = final_model.predict([np.array([image]), np.array(par_caps)])
            word_preds = np.argsort(preds[0])[-beam_index:]
            for w in word_preds:
                next_cap, prob = s[0][:], s[1]
                next_cap.append(w)
                prob += preds[0][w]
                temp.append([next_cap, prob])                    
        start_word = temp
        start_word = sorted(start_word, reverse=False, key=lambda l: l[1])
        start_word = start_word[-beam_index:]
    
    start_word = start_word[-1][0]
    intermediate_caption = [idx2word[i] for i in start_word]
    final_caption = []
    
    for i in intermediate_caption:
        if i != '<end>':
            final_caption.append(i)
        else:
            break
    final_caption = ' '.join(final_caption[1:])
    return final_caption

class Main:
    
    def __init__(self, w_idx_path, idx_w_path, weights_path):
        self.word2idx = pickle.load(open(w_idx_path, 'rb'))
        self.idx2word = pickle.load(open(idx_w_path, 'rb'))
        model = InceptionV3(weights='imagenet')
        new_input = model.input
        hidden_layer = model.layers[-2].output
        self.model_new = Model(new_input, hidden_layer)
        self.max_len = 40
        self.vocab_size = 8256
        embedding_size = 300
        image_model = Sequential([
                Dense(embedding_size, input_shape=(2048,), activation='relu'),
                RepeatVector(self.max_len)
            ])
        caption_model = Sequential([
                Embedding(self.vocab_size, embedding_size, input_length=self.max_len),
                LSTM(256, return_sequences=True),
                TimeDistributed(Dense(300))
            ])
        self.final_model = Sequential([
                Merge([image_model, caption_model], mode='concat', concat_axis=1),
                Bidirectional(LSTM(256, return_sequences=False)),
                Dense(self.vocab_size),
                Activation('softmax')
            ])
        self.final_model.load_weights(weights_path)
        
    def predict(self, img_path, flag=False, beam_size=None):
        if not flag:
            caption = predict_captions(encode(img_path, self.model_new), self.final_model, 
                                       self.word2idx, self.idx2word, self.max_len)
        else:
            caption = beam_search_predictions(encode(img_path, self.model_new),
                                              beam_size, self.final_model, 
                                              self.word2idx, self.idx2word, self.max_len)
        return caption