from agent import Agent
import math
from os import getenv, environ
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
import pickle as pk
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import layers
from tensorflow.keras.models import load_model
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

class CNNAgent(Agent):
    
    def __init__(self):
        super().__init__()
        load_dotenv(Path('.') / 'constants.env')
        self.model = self.build_model()
        self.states = []
    
    def update(self, data):
        self.cities = self.patch(self.cities, data['cities_diff'])
        self.map = self.patch(self.map, data['map_diff'])
        self.generals = data['generals']
        self.states.append(self.convert_map())    
    
    # TODO    
    def next_move(self):
        return 0, 0
    
    def build_model(self):
        max_map_dims = int(getenv('MAX_MAP_DIMS', default=32))
        max_map_size = max_map_dims**2
        input_ = keras.layers.input(shape=(max_map_dims, max_map_dims))
        layer1 = keras.layers.Conv2D(filters=64,kernel_size=6,strides=1,activation='relu',padding='same',input_shape=[max_map_dims,max_map_dims,8])(input_)
        layer2 = keras.layers.MaxPooling2D(pool_size=4,strides=2,padding='same')(layer1)
        layer3 = keras.layers.Conv2D(filters=128,kernel_size=5,strides=1,activation='relu',padding='same')(layer2)
        layer4 = keras.layers.MaxPooling2D(pool_size=4,strides=2,padding='same')(layer3)
        layer5 = keras.layers.Conv2D(filters=256,kernel_size=4,strides=1,activation='relu',padding='same')(layer4)
        layer6 = keras.layers.Conv2D(filters=256,kernel_size=4,strides=1,activation='relu',padding='same')(layer5)
        layer7 = keras.layers.MaxPooling2D(pool_size=4,strides=2,padding='same')(layer6)
        layer8 = keras.layers.Conv2D(filters=512,kernel_size=3,strides=1,activation='relu',padding='same')(layer7)
        layer9 = keras.layers.Conv2D(filters=512,kernel_size=3,strides=1,activation='relu',padding='same')(layer8)
        layer10 = keras.layers.MaxPooling2D(pool_size=4,strides=2,padding='same')(layer9)
        layer11 = keras.layers.Conv2D(filters=1024,kernel_size=2,strides=1,activation='relu',padding='same')(layer10)
        layer12 = keras.layers.Conv2D(filters=1024,kernel_size=2,strides=1,activation='relu',padding='same')(layer11)
        layer13 = keras.layers.MaxPooling2D(pool_size=4,strides=2,padding='same')(layer12)
        layer14 = keras.layers.Flatten()(layer13)
        layer15 = keras.layers.Dense(8192,activation='relu')(layer14) # TODO: add turn, scores to layer input
        layer16 = keras.layers.Dropout(0.5)(layer15)
        layer17 = keras.layers.Dense(8192,activation='relu')(layer16)
        layer18 = keras.layers.Dropout(0.5)(layer17)
        layer19 = keras.layers.Dense(4096,activation='relu')(layer18)
        layer20 = keras.layers.Dropout(0.5)(layer19)
        layer21 = keras.layers.Dense(4096,activation='relu')(layer20)
        layer22 = keras.layers.Dropout(0.5)(layer21)
        layer23 = keras.layers.Dense(2048,activation='relu')(layer22)
        layer24 = keras.layers.Dropout(0.5)(layer23)
        layer25 = keras.layers.Dense(1024,activation='relu')(layer24)
        layer26 = keras.layers.Dropout(0.5)(layer25)
        layer27 = keras.layers.Dense(512,activation='relu')(layer26)
        layer28 = keras.layers.Dropout(0.5)(layer27)
        output_position = keras.layers.Dense(max_map_size*2,activation='softmax')(layer28)
        output_direction = keras.layers.Dense(5,activation='softmax')(layer28)
        
        model = keras.Model(inputs=[input_], outputs=[output_position, output_direction])
        opt = keras.optimizers.Adam(learning_rate=0.0001)
        model.compile(optimizer=opt,loss='mean_squared_error') # TODO: define loss function
        return model
    
    def load_model(self, filename):
        saved_model = load_model(filename)
        return saved_model

    # TODO
    def train_model(self, input_filename):
        # Example code from a previous CNN
        kfold = KFold(n_splits=3, shuffle=True)
        fold_no = 1
        r_squared_vals = []
        for train, test in kfold.split(X_scaled, y):
            model = self.build_model()
            es = EarlyStopping(monitor='val_loss', verbose=2, patience=25)
            mc = ModelCheckpoint('best_model.h5', monitor='val_loss', mode='min', verbose=0, save_best_only=True)
            history = model.fit(X_scaled[train],y[train],validation_data=(X_scaled[test],y[test]),epochs=1000000,callbacks=[es,mc])
            # Generate metrics
            saved_model = load_model('best_model.h5')
            y_pred = saved_model.predict(X_scaled[test])
            y_true = y[test]
            r_square = r2_score(y_true, y_pred)
            r_squared_vals.append(r_square)
            fold_no = fold_no + 1
            return None
        
    # Converts the current map into a series of matrices for CNN analysis
    def convert_map(self):
        map_width, map_height, map_size, armies, terrain = self.read_map()
        terrain = np.array(terrain)
        armies = np.array(armies)
        empty_tiles = np.where(terrain==environ.get('TILE_EMPTY'), 0, 1)
        mountains = np.where(terrain==environ.get('TILE_MOUNTAIN'), 0, 1)
        fog = np.where(terrain==environ.get('TILE_FOG'), 0, 1)
        fog_obstacle = np.where(terrain==environ.get('TILE_FOG_OBSTACLE'), 0, 1)
        generals = self.indices_to_map(self.generals)
        cities = self.indices_to_map(self.cities)
        owned_armies = np.zeros(map_size)
        other_armies = np.zeros(map_size)
        for i in range(len(armies)):
            if terrain[i] not in [environ.get('TILE_EMPTY'), environ.get('TILE_MOUNTAIN'), \
                                    environ.get('TILE_FOG'), environ.get('TILE_FOG_OBSTACLE')]:
                if terrain[i] == self.player_index:
                    owned_armies[i] = armies[i]
                else:
                    other_armies[i] = armies[i]
        output = [empty_tiles, mountains, fog, fog_obstacle, generals, cities, owned_armies, other_armies]
        max_map_dims = int(getenv('MAX_MAP_DIMS', default=32))
        return [self.pad_map(item.reshape(map_height,map_width), (max_map_dims, max_map_dims)) for item in output]
    
    # Pad maps to the maximum dimensions    
    @staticmethod
    def pad_map(map, shape):
        left_pad = math.floor(shape[1] / 2)
        right_pad = shape[1] - left_pad
        top_pad = math.floor(shape[0] / 2)
        bottom_pad = shape[0] - top_pad
        mid = np.hstack((np.zeros((map.shape[0], left_pad)), np.array(map), np.zeros((map.shape[0], right_pad))))
        return np.vstack((np.zeros((top_pad, shape[1])), mid, np.zeros((bottom_pad, shape[1]))))
        