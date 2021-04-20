import numpy as np
from os import environ
from dotenv import load_dotenv
from pathlib import Path

class Agent:
    
    def __init__(self):
        load_dotenv(Path('.') / 'constants.env')
        self.player_index = None
        self.generals = None
        self.cities = []
        self.map = []
    
    def set_player_index(self, player_index):
        self.player_index = player_index
    
    def update(self, data):
        self.cities = self.patch(self.cities, data['cities_diff'])
        self.map = self.patch(self.map, data['map_diff'])
        self.generals = data['generals']
    
    def read_map(self):
        map_width = self.map[0]
        map_height = self.map[1]
        map_size = map_width * map_height
        armies = self.map[2:map_size+2]
        terrain = self.map[map_size+2:]
        return map_width, map_height, map_size, armies, terrain
        
    # Handles patch updates to arrays        
    @staticmethod        
    def patch(old, diff):
        out = []
        i = 0
        while i < len(diff):
            if diff[i] > 0:
                output_length = len(out)
                out = out + old[output_length:output_length+diff[i]]
            i += 1
            if i < len(diff):
                if diff[i] > 0:
                    num_mismatched = diff[i]
                    if i + num_mismatched + 1 >= len(diff):
                        out = out + diff[i+1:]
                    else:
                        out = out + diff[i+1:i+num_mismatched+1]
                    i += diff[i]
            i += 1
        return out
    
    # Convert list of indices to map-sized matrix containing ones and zeros
    def indices_to_map(self, indices):
        output = np.zeros(self.map[0]*self.map[1])
        for i in indices:
            if i > 0:
                output[i] = 1
        return output