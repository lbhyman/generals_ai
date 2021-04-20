import random as rnd
import math
from agent import Agent

class RandomAgent(Agent):
    
    def __init__(self):
        super().__init__()
        
    def next_move(self):
        map_width, map_height, map_size, armies, terrain = self.read_map()
        count = 0
        while(count < 100000):
            count += 1
            start_index = rnd.randrange(0, map_size)
            end_index = start_index
            if terrain[start_index] == self.player_index:
                row = math.floor(start_index / map_width)
                col = start_index % map_width
                rand_direction = rnd.random()
                if rand_direction <= 0.25 and col > 0:
                    end_index -= 1
                elif 0.25 < rand_direction <= 0.5 and col < map_width - 1:
                    end_index += 1
                elif 0.5 < rand_direction <= 0.75 and row < map_height - 1:
                    end_index += map_width
                elif rand_direction > 0.75 and row > 0:
                    end_index -= map_width
                else:
                    continue
                return start_index, end_index
        return 0, 0