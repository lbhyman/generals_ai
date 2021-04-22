import unittest
import sys
import os
sys.path.append(os.path.abspath('../'))
from simulated_game import SimulatedGame

class TestSimulatedGame(unittest.TestCase):
    
    def setUp(self):
        self.game = SimulatedGame()
        
    def tearDown(self):
        pass
    
    def test_get_diff(self):
        diff = self.game.get_diff([], [1,4,7,2,7,9])
        self.assertEqual(diff, [0,6,1,4,7,2,7,9])
        diff = self.game.get_diff([1,1,1,1], [1,1,1,2,3,3,3,3])
        self.assertEqual(diff, [3,5,2,3,3,3,3])
        diff = self.game.get_diff([1,1,1,1,1,4,4,4,4,4], [1,1,1,2,3,4,4,4,5,5,6])
        self.assertEqual(diff, [3,2,2,3,3,3,5,5,6])
        
if __name__ == '__main__':
    unittest.main()