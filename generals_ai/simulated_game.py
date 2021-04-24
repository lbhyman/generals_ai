import json
import numpy as np
from player import Player
from CNN_agent import CNNAgent
from random_agent import RandomAgent
from os import getenv, environ
import random as rnd
import math


class SimulatedGame():

    def __init__(self, previous_state=None, replay_filename=None):
        self.map_dimensions = []
        self.players = []
        self.cities = []
        self.mountains = []
        self.generals = []
        self.armies = []
        self.turn = 0
        self.initialize_randomly()
        '''while not self.screen_map():
            self.initialize_randomly()'''

    def initialize_randomly(self):
        num_players = 2
        width = 16 + num_players + \
            round((rnd.random()**2) * (4 + (num_players / 2)))
        height = 16 + num_players + \
            round((rnd.random()**2) * (4 + (num_players / 2)))
        map_size = width * height
        self.map_dimensions = [height, width]
        self.players = [RandomAgent(), RandomAgent()]
        self.cities = np.zeros(map_size)
        self.mountains = np.zeros(map_size)
        self.generals = np.zeros(map_size)
        self.armies = np.zeros(map_size)
        for i in range(num_players):
            index = rnd.randrange(map_size)
            self.generals[index] = i
            self.armies[index] = 1
        for i in range(map_size):
            if rnd.random() < 0.15 and self.generals[i] == 0:
                self.mountains[i] = 1
            elif rnd.random() < 0.1 and self.generals[i] == 0:
                self.cities[i] = 1
                self.armies[i] = rnd.randrange(35, 50)

    def screen_map(self):
        indices = []
        for i in range(self.map_dimensions[0] * self.map_dimensions[1]):
            if self.generals[i] > 0:
                indices.append(i)
        for i in range(len(indices)):
            general = self.generals[i]
            row = math.floor(general / self.map_dimensions[1])
            col = general % self.map_dimensions[1]
            other_generals = self.generals[0:max(
                i, 1)] + self.generals[min(i+1, len(self.generals)-1):len(self.generals)]
            for other_general in other_generals:
                other_row = math.floor(other_general / self.map_dimensions[1])
                other_col = other_general % self.map_dimensions[1]
                distance = np.linalg.norm(
                    np.array((row, col)) - np.array((other_row, other_col)))
                min_distance = 0.25 * \
                    np.linalg.norm(
                        np.array((self.map_dimensions[0], self.map_dimensions[1])) - np.array((0, 0)))
                if distance < min_distance:
                    return False
        return True

    # Take a list of dict objects representing each players' action in a turn, and update the
    # maps and players accordingly
    def process_player_moves(self, moves):
        for move in moves:
            player_index = move['index']
            start_position = self.indices_to_map_positions([move['start']])
            end_position = self.indices_to_map_positions([move['end']])
            move_size = math.floor(
                np.max(np.sum(np.multiply(start_position, self.armies[player_index+1])) - 1, 0))
            # Check if player has split army in half
            if move['is50'] == 1:
                move_size = math.floor(move_size / 2)
            # Test if attempting to move into a mountain, do nothing if so
            if np.multiply(end_position, self.mountains).any():
                break
            # Remove player's moved army count from start position
            self.armies[player_index + 1] = np.subtract(
                self.armies[player_index + 1], start_position * move_size)
            # Identify attacks
            enemy_army_index = -1
            enemy_army_size = 0
            for i in range(len(self.armies)):
                enemy_army_size = np.sum(
                    np.multiply(end_position, self.armies[i]))
                if enemy_army_size > 0 and i != player_index + 1:
                    enemy_army_index = i
                    break
            # Move to empty or friendly square
            if enemy_army_index == -1:
                self.armies[player_index+1] = np.add(
                    self.armies[player_index + 1], end_position * move_size)
            # Take enemy square
            elif move_size > enemy_army_size:
                self.armies[enemy_army_index] = np.subtract(
                    self.armies[enemy_army_index], end_position * math.floor(enemy_army_size))
                self.armies[player_index+1] = np.add(self.armies[player_index + 1], end_position * (
                    move_size - math.floor(enemy_army_size)))
                # Check if captured a general
                if np.sum(np.multiply(end_position, self.generals)) > 0:
                    self.players[player_index].increment_generals(1)
                    self.players[enemy_army_index - 1].increment_generals(-1)
                    # Take enemy's land if dead
                    if not self.players[enemy_army_index - 1].alive:
                        self.armies[player_index+1] = np.add(
                            self.armies[player_index + 1], self.armies[enemy_army_index])
                        self.armies[enemy_army_index] = np.subtract(
                            self.armies[enemy_army_index], self.armies[enemy_army_index])
            # Enemy maintains square
            elif move_size < enemy_army_size:
                self.armies[enemy_army_index] = np.subtract(
                    self.armies[enemy_army_index], end_position * (move_size))
            # If army sizes are identical, enemy maintains 0.1 army for recordkeeping (can grow later)
            else:
                self.armies[enemy_army_index] = np.subtract(
                    self.armies[enemy_army_index], end_position * (enemy_army_size - 0.1))

    # Map a list of indices in a gioreplay file to numpy arrays for convolutional network analysis
    def indices_to_map_positions(self, indices, values=[]):
        list_length = self.map_dimensions[0]*self.map_dimensions[1]
        output = np.zeros(list_length)
        if len(values) == 0:
            values = [1]*len(indices)
        for i in range(len(indices)):
            output[indices[i]] = values[i]
        return np.reshape(output, (self.map_dimensions[0], self.map_dimensions[1]))

    # Handle the entire turn, including player actions and periodic army gains
    def handle_turn(self, turn, moves):
        self.process_player_moves(moves)
        # Players periodically gain armies from owned land, cities, and generals
        # All owned land increases armies
        if turn > 0 and turn % 50 == 0:
            for i in range(len(self.armies)):
                self.armies[i] = np.where(
                    self.armies[i] > 0, self.armies[i] + 1, self.armies[i])
        # Generals and cities increase armies
        elif turn > 0 and turn % 2 == 0:
            for i in range(len(self.armies)):
                increment = np.add(np.multiply(self.armies[i], self.generals), np.multiply(
                    self.armies[i], self.cities))
                increment[increment > 0] = 1
                self.armies[i] = np.add(self.armies[i], increment)
        # Calculate player scores
        for i in range(len(self.players)):
            army_size = math.floor(np.sum(self.armies[i+1]))
            land_size = math.floor(np.count_nonzero(self.armies[i+1]))
            self.players[i].set_army(army_size)
            self.players[i].set_land(land_size)

    # Return all visible channels from a player's perspective
    def get_player_visibilities(self, player_index):
        output = []
        # Self.armies[0] denotes neutral armies, player_index starts at 0
        army = self.armies[1+player_index]
        player_visibility = self.get_visible_cells(army)
        fog = np.subtract(np.ones(army.shape), player_visibility)
        output = output + [player_visibility, fog, np.multiply(self.cities, player_visibility),
                           np.multiply(self.mountains, player_visibility), np.multiply(self.generals, player_visibility)]
        for i in range(len(self.armies)):
            output = output + \
                [np.multiply(self.armies[i], player_visibility)]
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
            rows = [row-1, row, row+1]
            cols = [col-1, col, col+1]
            for j in rows:
                for k in cols:
                    if 0 <= j < matrix_dimensions[0] and 0 <= k < matrix_dimensions[1]:
                        output_matrix[j][k] = 1
        return output_matrix

    # Helper function to get the difference between two arrays, simulating the generals.io server packets
    @staticmethod
    def get_diff(old_matrix, new_matrix):
        old_array = np.array(old_matrix).flatten().tolist()
        new_array = np.array(new_matrix).flatten().tolist()
        output = []
        i = 0
        while i < len(new_array):
            matching = 0
            while i < len(new_array) and i < len(old_array) and old_array[i] == new_array[i]:
                matching += 1
                i += 1
            output.append(matching)
            mismatching = []
            while i < len(new_array):
                if i >= len(old_array):
                    mismatching.append(new_array[i])
                    i += 1
                elif old_array[i] != new_array[i]:
                    mismatching.append(new_array[i])
                    i += 1
                else:
                    break
            output.append(len(mismatching))
            output = output + mismatching
        return output

    # Based on each player's visibility, produce a map the server would send to them
    def get_player_maps(self):
        output = []
        for i in range(len(self.players)):
            map = np.full(shape=self.map_dimensions, fill_value=int(environ.get('TILE_EMPTY', -1)))
            # Process terrain
            vis = self.get_player_visibilities(i)
            visibility, fog, visible_cities, visible_mountains, visible_generals = vis[:5]
            fog_obstacle = np.multiply(fog, np.add(self.mountains, self.cities)) * \
                (int(environ.get('TILE_FOG_OBSTACLE', -4)) - int(environ.get('TILE_EMPTY', -1)))
            fog = fog * (int(environ.get('TILE_FOG', -3)) - int(environ.get('TILE_EMPTY', -1)))
            visible_mountains = visible_mountains * (int(environ.get('TILE_MOUNTAIN', -2)) - \
                int(environ.get('TILE_EMPTY', -1)))
            map = map + fog_obstacle + fog + visible_mountains
            # Process armies
            for visible_army in vis[5:]:
                # TODO
                map = map + visible_army
            output.append(map)
        return output
