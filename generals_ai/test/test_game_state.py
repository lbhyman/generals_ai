import unittest
import sys
import os
sys.path.append(os.path.abspath('../'))
from game_state import GameState
import numpy as np

class TestGameState(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()
        self.game_state.set_map_dimensions([3,5])
        self.test_input_filename = '../data/test_replay.gioreplay'

    def tearDown(self):
        pass

    def test_set_map_dimensions(self):
        self.assertEqual(self.game_state.map_dimensions, [3,5])
        self.game_state.set_map_dimensions([2,6])
        self.assertEqual(self.game_state.map_dimensions, [2,6])
        
    def test_indices_to_map_positions(self):
        output = self.game_state.indices_to_map_positions([0,1,4,5,6,14])
        desired = np.array([[1,1,0,0,1],[1,1,0,0,0],[0,0,0,0,1]])
        self.assertTrue(np.array_equal(output, desired))
        
    def test_initialize_from_repay_file(self):
        self.game_state = GameState()
        self.game_state.initialize_from_replay_file(self.test_input_filename)
        self.assertEqual(self.game_state.map_dimensions, [3,5])
        self.assertEqual([player.name for player in self.game_state.players], ["user_1","user_2","user_3"])
        self.assertTrue(np.array_equal(self.game_state.cities, \
            np.array([[1,0,0,0,0],[0,0,0,0,0],[0,0,0,0,1]])))
        self.assertTrue(np.array_equal(self.game_state.mountains, \
            np.array([[0,0,0,1,0],[0,0,0,1,0],[0,0,0,0,0]])))
        self.assertTrue(np.array_equal(self.game_state.generals, \
            np.array([[0,0,0,0,0],[0,1,0,0,1],[0,0,1,0,0]])))
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[45,0,0,0,0],[0,0,0,0,0],[0,0,0,0,22]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]], \
            [[0,0,0,0,0],[0,1,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0]] \
            ])))
        
    def test_transfer_from_previous(self):
        self.previous_game_state = GameState()
        self.previous_game_state.initialize_from_replay_file(self.test_input_filename)
        self.new_game_state = GameState()
        self.new_game_state.transfer_from_previous(self.previous_game_state)
        self.assertTrue(np.array_equal(self.previous_game_state.map_dimensions, self.new_game_state.map_dimensions))
        self.assertTrue(np.array_equal(self.previous_game_state.cities, self.new_game_state.cities))
        self.assertTrue(np.array_equal(self.previous_game_state.mountains, self.new_game_state.mountains))
        self.assertTrue(np.array_equal(self.previous_game_state.generals, self.new_game_state.generals))
        self.assertTrue(np.array_equal(self.previous_game_state.armies, self.new_game_state.armies))
        
    def test_process_player_moves(self):
        self.game_state.initialize_from_replay_file(self.test_input_filename)
        for i in range(100):
            self.game_state.handle_turn(i,[])
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[94,0,0,0,0],[0,0,0,0,0],[0,0,0,0,71]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,50,0,0]], \
            [[0,0,0,0,0],[0,50,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,50],[0,0,0,0,0]] \
            ])))
        moves = [{"index":0,"start":12,"end":13,"is50":0,"turn":101}]
        self.game_state.process_player_moves(moves)
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[94,0,0,0,0],[0,0,0,0,0],[0,0,0,0,71]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,49,0]], \
            [[0,0,0,0,0],[0,50,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,50],[0,0,0,0,0]] \
            ])))
        # Attack city and lose
        moves = [{"index":0,"start":13,"end":14,"is50":0,"turn":101}]
        self.game_state.process_player_moves(moves)
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[94,0,0,0,0],[0,0,0,0,0],[0,0,0,0,23]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,1,0]], \
            [[0,0,0,0,0],[0,50,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,50],[0,0,0,0,0]] \
            ])))
        # Move into mountain
        moves = [{"index":1,"start":6,"end":7,"is50":0,"turn":101},
                 {"index":1,"start":7,"end":8,"is50":0,"turn":101},
                 {"index":1,"start":7,"end":8,"is50":0,"turn":101}]
        self.game_state.process_player_moves(moves)
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[94,0,0,0,0],[0,0,0,0,0],[0,0,0,0,23]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,1,0]], \
            [[0,0,0,0,0],[0,1,49,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,50],[0,0,0,0,0]] \
            ])))
        # Take Enemy general
        moves = [{"index":2,"start":9,"end":10,"is50":0,"turn":101},
                 {"index":2,"start":10,"end":11,"is50":0,"turn":101},
                 {"index":2,"start":11,"end":12,"is50":0,"turn":101}]
        self.game_state.process_player_moves(moves)
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[94,0,0,0,0],[0,0,0,0,0],[0,0,0,0,23]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,1,49,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,1],[1,1,46,1,0]] \
            ])))
        self.assertFalse(self.game_state.players[0].alive)
        self.assertTrue(self.game_state.players[2].alive)
        self.assertTrue(self.game_state.players[1].alive)
        self.assertEqual(self.game_state.players[2].generals, 2)
        self.assertEqual(self.game_state.players[0].generals, 0)
        self.assertEqual(self.game_state.players[1].generals, 1)
        # TODO: test more cases (take general with equivalent army size, split army)
        
    def test_handle_turn(self):
        self.game_state.initialize_from_replay_file(self.test_input_filename)
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[45,0,0,0,0],[0,0,0,0,0],[0,0,0,0,22]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]], \
            [[0,0,0,0,0],[0,1,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0]] \
            ])))
        self.game_state.handle_turn(0,[])
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[45,0,0,0,0],[0,0,0,0,0],[0,0,0,0,22]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]], \
            [[0,0,0,0,0],[0,1,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0]] \
            ])))
        self.game_state.handle_turn(1,[])
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[45,0,0,0,0],[0,0,0,0,0],[0,0,0,0,22]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0]], \
            [[0,0,0,0,0],[0,1,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0]] \
            ])))
        self.game_state.handle_turn(2,[])
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[46,0,0,0,0],[0,0,0,0,0],[0,0,0,0,23]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,2,0,0]], \
            [[0,0,0,0,0],[0,2,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,2],[0,0,0,0,0]] \
            ])))
        self.game_state.handle_turn(50,[])
        self.assertTrue(np.array_equal(self.game_state.armies, \
            np.array([ \
            [[47,0,0,0,0],[0,0,0,0,0],[0,0,0,0,24]], \
            [[0,0,0,0,0],[0,0,0,0,0],[0,0,3,0,0]], \
            [[0,0,0,0,0],[0,3,0,0,0],[0,0,0,0,0]], \
            [[0,0,0,0,0],[0,0,0,0,3],[0,0,0,0,0]] \
            ])))
    
    # TODO   
    def test_get_player_visibilities(self):
        return None
    
    # TODO   
    def test_get_visible_cells(self):
        return None
        
if __name__ == '__main__':
    unittest.main()