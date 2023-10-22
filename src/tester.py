from maze_clause import *
from maze_knowledge_base import *
from maze_agent import *


class Tester:
    @staticmethod
    def test():
        #    c-> 012345   # r
        maze = ["XXXXXX", # 0
                "X...GX", # 1
                "X..PPX", # 2
                "X....X", # 3
                "X..P.X", # 4
                "X@...X", # 5
                "XXXXXX"] # 6
        env = Environment(maze, tick_length = 0, verbose = False)
        # The starting tile should be known as safe
        print("True" + str(env.test_safety_check((1,5))))
         
        # Given that the perception will be a 0 tile on the initial space, we also
        # know that surrounding tiles are
        print("True" + str(env.test_safety_check((1,4))))
        print("True" + str(env.test_safety_check((2,5))))
        
        # If that's the only perception, however, other tiles won't be known safe
        print("None" + str(env.test_safety_check((2,4))))
        print("None" + str(env.test_safety_check((4,2))))
         
        # Still, the goal should always be safe
        print("True" + str(env.test_safety_check((4,1))))
        
    
Tester.test()