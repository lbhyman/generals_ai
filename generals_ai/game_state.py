import json
import numpy as np
from player import Player
import math

# Holds all relevant maps that will be processed by the CNN
class GameState:
    
    # Empty gamestate with two initialization options
    def __init__(self, previous_state=None, replay_filename=None):
        self.map_dimensions = []
        self.players = []
        self.cities = []
        self.mountains = []
        self.generals = []
        self.armies = []
        self.turn = 0
        if previous_state is not None:
            self.transfer_from_previous(previous_state)
        elif replay_filename is not None:
            self.initialize_from_replay_file(replay_filename)
       
    def set_map_dimensions(self,dimensions):
        self.map_dimensions = dimensions
    
    # Copy a gamestate's parameters to the current instance   
    def transfer_from_previous(self, previous_state):
        if previous_state is not None:
            self.map_dimensions, self.players, self.cities, self.mountains, self.generals ,self.armies = \
                previous_state.map_dimensions, previous_state.players, previous_state.cities, \
                previous_state.mountains, previous_state.generals, previous_state.armies
    
    # Initialize the gamestate from a .gioreplay file at turn 0 
    def initialize_from_replay_file(self, replay_filename):
        try:
            input_file = open(replay_filename, 'r')
        except IOError:
            return
        try:
            data = json.load(input_file)
            # Dimensions
            self.map_dimensions = [data['mapHeight'], data['mapWidth']]
            # Players
            for i in range(len(data['usernames'])):
                name = data['usernames'][i]
                stars = data['stars'][i]
                self.players.append(Player(name,stars))
            # Cities
            self.cities = self.indices_to_map_positions(data['cities'])
            # Mountains
            self.mountains = self.indices_to_map_positions(data['mountains'])
            # Generals
            self.generals = self.indices_to_map_positions(data['generals'])
            # Neutral armies
            self.armies.append(self.indices_to_map_positions(data['cities'],data['cityArmies']))
            # Player armies
            for i in range(len(self.players)):
                self.armies.append(self.indices_to_map_positions([data['generals'][i]]))
            input_file.close()
        except:
            input_file.close()
    
    # Map a list of indices in the gioreplay file to numpy arrays for convolutional network analysis
    def indices_to_map_positions(self, indices, values=[]):
        list_length = self.map_dimensions[0]*self.map_dimensions[1]
        output = np.zeros(list_length)
        if len(values) == 0:
            values = [1]*len(indices)
        for i in range(len(indices)):
            output[indices[i]] = values[i]
        return np.reshape(output, (self.map_dimensions[0], self.map_dimensions[1]))
    
    # Take a list of dict objects representing each players' action in a turn, and update the
    # maps and players accordingly
    def process_player_moves(self, moves):
        for move in moves:
            player_index = move['index']
            start_position = self.indices_to_map_positions([move['start']])
            end_position = self.indices_to_map_positions([move['end']])
            move_size = math.floor(np.max(np.sum(np.multiply(start_position,self.armies[player_index+1])) - 1, 0))
            # Check if player has split army in half
            if move['is50'] == 1:
                move_size = math.floor(move_size / 2)
            # Test if attempting to move into a mountain, do nothing if so
            if np.multiply(end_position,self.mountains).any():
                break
            # Remove player's moved army count from start position
            self.armies[player_index + 1] = np.subtract(self.armies[player_index + 1], start_position * move_size)
            # Identify attacks
            enemy_army_index = -1
            enemy_army_size = 0
            for i in range(len(self.armies)):
                enemy_army_size = np.sum(np.multiply(end_position, self.armies[i]))
                if enemy_army_size > 0 and i != player_index + 1:
                    enemy_army_index = i
                    break
            # Move to empty or friendly square
            if enemy_army_index == -1:
                self.armies[player_index+1] = np.add(self.armies[player_index + 1], end_position * move_size)
            # Take enemy square
            elif move_size > enemy_army_size:
                self.armies[enemy_army_index] = np.subtract(self.armies[enemy_army_index], end_position * math.floor(enemy_army_size))
                self.armies[player_index+1] = np.add(self.armies[player_index + 1], end_position * (move_size - math.floor(enemy_army_size)))
                # Check if captured a general
                if np.sum(np.multiply(end_position, self.generals)) > 0:
                    self.players[player_index].increment_generals(1)
                    self.players[enemy_army_index - 1].increment_generals(-1)
                    # Take enemy's land if dead
                    if not self.players[enemy_army_index - 1].alive:
                        self.armies[player_index+1] = np.add(self.armies[player_index + 1], self.armies[enemy_army_index])
                        self.armies[enemy_army_index] = np.subtract(self.armies[enemy_army_index], self.armies[enemy_army_index])                                    
            # Enemy maintains square
            elif move_size < enemy_army_size:
                self.armies[enemy_army_index] = np.subtract(self.armies[enemy_army_index], end_position * (move_size))
            # If army sizes are identical, enemy maintains 0.1 army for recordkeeping (can grow later)
            else:
                self.armies[enemy_army_index] = np.subtract(self.armies[enemy_army_index], end_position * (enemy_army_size - 0.1))
    
    # Handle the entire turn, including player actions and periodic army gains
    def handle_turn(self, turn, moves):
        self.process_player_moves(moves)
        # Players periodically gain armies from owned land, cities, and generals
        # All owned land increases armies
        if turn > 0 and turn % 50 == 0:
            for i in range(len(self.armies)):
                self.armies[i] = np.where(self.armies[i] > 0, self.armies[i] + 1, self.armies[i])
        # Generals and cities increase armies
        elif turn > 0 and turn % 2 == 0:
            for i in range(len(self.armies)):
                increment = np.add(np.multiply(self.armies[i],self.generals),np.multiply(self.armies[i],self.cities))
                increment[increment > 0] = 1
                self.armies[i] = np.add(self.armies[i], increment)
        # Calculate player scores
        for i in range(len(self.players)):
            army_size = math.floor(np.sum(self.armies[i+1]))
            land_size = math.floor(np.count_nonzero(self.armies[i+1]))
            self.players[i].set_army(army_size)
            self.players[i].set_land(land_size)
    
    # Return all visible channels from each player's perspective      
    def get_player_visibilities(self):
        output = []
        for army in self.armies[1:]:
            player_visibility = self.get_visible_cells(army)
            fog = np.subtract(np.ones(army.shape), player_visibility)
            output = output + [fog,np.multiply(self.cities,player_visibility), \
                np.multiply(self.mountains,player_visibility),np.multiply(self.generals,player_visibility)]
            for i in range(len(self.armies)):
                output = output + [np.multiply(self.armies[i],player_visibility)]
        return output
    
    # Return a matrix indicating visible cells to a player
    @staticmethod
    def get_visible_cells(matrix):
        matrix_dimensions = np.shape(matrix)
        output_matrix = np.zeros(matrix_dimensions)
        owned_elements = np.nonzero(matrix)
        for i in range(owned_elements.shape[0]):
            row = owned_elements[0][i]
            col = owned_elements[1][i]
            rows = [row-1,row,row+1]
            cols = [col-1,col,col+1]
            for j in rows:
                for k in cols:
                    if 0 <= j < matrix_dimensions[0] and 0 <= k < matrix_dimensions[1]:
                        output_matrix[j][k] = 1
        return output_matrix