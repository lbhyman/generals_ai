from game_replay import GameReplay
from game_state import GameState
import sys
import json
import glob

output_filename = '../data/all_replays.json'

def main():
    try:
        file = open(output_filename, 'w')
    except IOError:
        print('Error writing output file')
        sys.exit(1)
    try:
        states = []
        for name in glob.glob('../data/*.gioreplay'):
            print(name)
            replay = GameReplay(filename = name)
            print(len(replay.states))
            for state in replay.states:
                states.append(state.__dict__)
        output = json.dumps(states)
        #print(output)
        file.write(output)
        file.close()
    except:
        file.close()

if __name__ == '__main__':
    main()
