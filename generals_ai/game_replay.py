import json
from game_state import GameState

class GameReplay:
    
    def __init__(self, states = [], max_turns = 2000):
        self.states = states
        self.max_turns = max_turns
    
    def get_states(self):
        return self.states
    
    def get_state(self, turn_index):
        return self.states[turn_index]
    
    def set_state(self, state):
        self.states = state
        
    def addstates(self,states):
        self.states.append(states)
    
    # Load replay from .gioreplay file   
    def load_game(self, filename):
        # Load initial gamestate
        initial_state = GameState(replay_filename=filename)
        self.states.append(initial_state)
        # Load moves and save additional gamestates
        try:
            input_file = open(filename, 'r')
        except IOError:
            return
        try:
            data = json.load(input_file)
            moves = data['moves']
            for turn in range(self.max_turns):
                current_moves = []
                for move in moves:
                    if move.turn == turn:
                        current_moves.append(move)
                previous_gamestate = self.states[-1]
                next_gamestate = GameState(previous_state=previous_gamestate)
                next_gamestate.handle_turn(turn, current_moves)
                self.states.append(next_gamestate)
            input_file.close()
        except:
            input_file.close()
    
    # TODO    
    def write_replay_vectors(self, filename):
        return None