import time
import random
import math
from queue import Queue
from constants import *
from maze_clause import *
from maze_knowledge_base import *

class MazeAgent:
    '''
    BlindBot MazeAgent meant to employ Propositional Logic,
    Planning, and Active Learning to navigate the Pitsweeper
    Problem. Have fun!
    '''
    
    def __init__ (self, env: "Environment", perception: dict) -> None:
        """
        Initializes the MazeAgent with any attributes it will need to
        navigate the maze.
        [!] Add as many attributes as you see fit!
        
        Parameters:
            env (Environment):
                The Environment in which the agent is operating; make sure
                to see the spec / Environment class for public methods that
                your agent will use to solve the maze!
            perception (dict):
                The starting perception of the agent, which is a
                small dictionary with keys:
                  - loc:  the location of the agent as a (c,r) tuple
                  - tile: the type of tile the agent is currently standing upon
        """
        self.env: "Environment" = env
        self.goal: tuple[int, int] = env.get_goal_loc()
        
        # The agent's maze can be manipulated as a tracking mechanic
        # for what it has learned; changes to this maze will be drawn
        # by the environment and is simply for visuals / debugging
        # [!] Feel free to change self.maze at will
        self.maze: list = env.get_agent_maze()
        
        # Standard set of attributes you'll want to maintain
        self.kb: "MazeKnowledgeBase" = MazeKnowledgeBase()
        self.possible_pits: set[tuple[int, int]] = set() 
        self.safe_tiles: set[tuple[int, int]] = set()
        self.pit_tiles: set[tuple[int, int]] = set()
        
        self.visited_tiles: set[tuple[int, int]] = set()
        
        #We know goal tile and adjacent tiles are safe
        self.add_Pit(self.env.get_goal_loc(), False)
        self.safe_tiles.add(self.env.get_goal_loc())
        adjGoalLocations = self.env.get_cardinal_locs(self.env.get_goal_loc(), 1)
        if len(adjGoalLocations) == 1:
            for adjacentLocation in self.env.get_cardinal_locs(self.env.get_goal_loc(), 1):
                self.add_Pit(adjacentLocation, False)
                self.safe_tiles.add(adjacentLocation)    
        
        self.think(perception)
        
        
    ##################################################################
    # Methods
    ##################################################################
    
    def think(self, perception: dict) -> tuple[int, int]:
        """
        The main workhorse method of how your agent will process new information
        and use that to make deductions and decisions. In gist, it should follow
        this outline of steps:
        1. Process the given perception, i.e., the new location it is in and the
           type of tile on which it's currently standing (e.g., a safe tile, or
           warning tile like "1" or "2")
        2. Update the knowledge base and record-keeping of where known pits and
           safe tiles are located, as well as locations of possible pits.
        3. Query the knowledge base to see if any locations that possibly contain
           pits can be deduced as safe or not.
        4. Use all of the above to prioritize the next location along the frontier
           to move to next.
        
        Parameters:
            perception (dict):
                A dictionary providing the agent's current location
                and current tile type being stood upon, of the format:
                {"loc": (x, y), "tile": tile_type}
        
        Returns:
            tuple[int, int]:
                The maze location along the frontier that your agent will try to
                move into next.
        """
        
        # print("Think Operation:     " + "KB Size: " + str(len(self.kb)))
        # print(" Landed on " + perception["tile"] + " tile on location " + str(perception["loc"]))
        # print("     possible_pits before:")
        # for tile in self.possible_pits:
        #     print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        # print("     safe_tiles before:")
        # for tile in self.safe_tiles:
        #     print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        # print("     pit_tiles before:")
        # for tile in self.pit_tiles:
        #     print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        
        frontier = self.env.get_frontier_locs()
        
        # print("     Safe Frontier Pits:")
        # for tile in frontier:
        #     if tile in self.safe_tiles:
        #         print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        
        if perception["tile"] == "1":
            adjTiles: dict[int : tuple[int, int]] = dict()
            adjLocations = self.env.get_cardinal_locs(perception['loc'], 1)
            
            counter = 0
            pitFound = False
            pit = (-32768, -32768)
            for adjacentLocation in adjLocations:
                if not pitFound:                    
                    if adjacentLocation in self.possible_pits:
                        self.pit_tiles.add(adjacentLocation)
                        self.add_Pit(adjacentLocation, True)
                        pit = adjacentLocation
                        pitFound = True
                    elif adjacentLocation in self.pit_tiles:
                        pit = adjacentLocation
                        pitFound = True
                    elif adjacentLocation not in self.visited_tiles or adjacentLocation not in self.safe_tiles or len(self.visited_tiles) == 0:
                        self.possible_pits.add(adjacentLocation)
                        adjTiles[counter] = adjacentLocation
                        counter += 1
            
            if pitFound == True:
                for adjacentLocation in adjLocations:
                    if adjacentLocation != pit:
                        self.safe_tiles.add(adjacentLocation)
                        if adjacentLocation in self.possible_pits:
                            self.possible_pits.remove(adjacentLocation)
                        self.add_Pit(adjacentLocation, False)
            elif counter == 1:
                for location in adjTiles.values():
                    self.pit_tiles.add(location)
                    self.add_Pit(location, True)
                    
            elif counter == 2:
                #prop1: (x or y)
                prop1 = set()
                prop1.add((("P", adjTiles[0]), True))
                prop1.add((("P", adjTiles[1]), True))
                self.kb.tell(MazeClause(prop1))
                
                #prop2: (not x or not y)
                prop2 = set()
                prop2.add((("P", adjTiles[0]), False))
                prop2.add((("P", adjTiles[1]), False))
                self.kb.tell(MazeClause(prop2))
            
            elif counter == 3:
                #prop1: (not x or not y)
                prop1 = set()
                prop1.add((("P", adjTiles[0]), False))
                prop1.add((("P", adjTiles[1]), False))
                self.kb.tell(MazeClause(prop1))
                
                #prop2: (not x or not z)
                prop2 = set()
                prop2.add((("P", adjTiles[0]), False))
                prop2.add((("P", adjTiles[2]), False))
                self.kb.tell(MazeClause(prop2))
                
                #prop3: (not y or not z)
                prop3 = set()
                prop3.add((("P", adjTiles[1]), False))
                prop3.add((("P", adjTiles[2]), False))
                self.kb.tell(MazeClause(prop3))
                
                #prop4: (x or y or z)
                prop4 = set()
                prop4.add((("P", adjTiles[0]), True))
                prop4.add((("P", adjTiles[1]), True))
                prop4.add((("P", adjTiles[2]), True))
                self.kb.tell(MazeClause(prop4))

            elif counter == 4:
                print("Too unreasonable to write out all of proposition logic")
                # CNF looks like (B ∨ A ∨ C ∨ D) ∧ (¬D ∨ A ∨ C ∨ ¬B) ∧ 
                # (¬D ∨ C ∨ ¬B) ∧ (¬C ∨ A ∨ ¬B) ∧ (¬D ∨ A ∨ ¬B) ∧ 
                # (¬A ∨ ¬B) ∧ (¬C ∨ ¬B) ∧ (¬D ∨ ¬B) ∧ (B ∨ ¬C ∨ ¬A) ∧ 
                # (¬A ∨ ¬C) ∧ (B ∨ A ∨ ¬D ∨ ¬C) ∧ (¬C ∨ A ∨ ¬D) ∧ 
                # (¬D ∨ A ∨ ¬C) ∧ (B ∨ ¬C ∨ ¬D) ∧ (¬C ∨ ¬D) ∧ (B ∨ ¬D ∨ ¬C) ∧ 
                # (B ∨ ¬D ∨ C ∨ ¬A) ∧ (¬D ∨ C ∨ ¬A) ∧ (B ∨ ¬D ∨ ¬A) ∧ (¬A ∨ ¬D)
                
                #Unrealistic to write all of that
                    
            self.kb.simplify_self(self.pit_tiles, self.safe_tiles)
            self.safe_tiles.add(perception['loc'])
            self.add_Pit(perception["loc"], False)
        elif perception["tile"] == "2":
            adjTiles: dict[int : tuple[int, int]] = dict()
            adjLocations = self.env.get_cardinal_locs(perception['loc'], 1)
            
            counter = 0
            pitFound = False
            pit1Found = False
            pit = (-32768, -32768)
            pit1 = (-32768, -32768)
            for adjacentLocation in adjLocations:
                if adjacentLocation in self.possible_pits and pitFound is False:
                    self.pit_tiles.add(adjacentLocation)
                    self.add_Pit(adjacentLocation, True)
                    pit = adjacentLocation
                    pitFound = True
                elif adjacentLocation in self.possible_pits and pitFound is True:
                    self.pit_tiles.add(adjacentLocation)
                    self.add_Pit(adjacentLocation, True)
                    pit1 = adjacentLocation
                    pit1Found = True
                elif adjacentLocation not in self.visited_tiles or adjacentLocation not in self.safe_tiles or len(self.visited_tiles) == 0:
                    self.possible_pits.add(adjacentLocation)
                    adjTiles[counter] = adjacentLocation
                    counter += 1
            
            if pitFound is True and pit1Found is False:        
                #Same as if the tile was "1"
                if counter == 1:
                    for location in adjTiles.values():
                        self.pit_tiles.add(location)
                        self.add_Pit(location, True)
                elif counter == 2:
                    #prop1: (x or y)
                    prop1 = set()
                    prop1.add((("P", adjTiles[0]), True))
                    prop1.add((("P", adjTiles[1]), True))
                    self.kb.tell(MazeClause(prop1))
                    
                    #prop2: (not x or not y)
                    prop2 = set()
                    prop2.add((("P", adjTiles[0]), False))
                    prop2.add((("P", adjTiles[1]), False))
                    self.kb.tell(MazeClause(prop2))
                
            elif pitFound is True and pit1Found is True:
                for adjacentLocation in adjLocations:
                    if adjacentLocation != pit and adjLocations != pit1:
                        self.safe_tiles.add(adjacentLocation)
                        if adjacentLocation in self.possible_pits:
                            self.possible_pits.remove(adjacentLocation)
            elif counter == 1 or counter == 2:
                for location in adjTiles.values():
                    self.pit_tiles.add(location)
                    self.add_Pit(location, True)
                    
            elif counter == 3:
                #prop1: (x or y)
                prop1 = set()
                prop1.add((("P", adjTiles[0]), True))
                prop1.add((("P", adjTiles[1]), True))
                self.kb.tell(MazeClause(prop1))
                
                #prop1: (x or z)
                prop2 = set()
                prop2.add((("P", adjTiles[0]), True))
                prop2.add((("P", adjTiles[2]), True))
                self.kb.tell(MazeClause(prop2))
                
                #prop1: (y or z)
                prop3 = set()
                prop3.add((("P", adjTiles[1]), True))
                prop3.add((("P", adjTiles[2]), True))
                self.kb.tell(MazeClause(prop3))
                
                #prop4: 
                prop4 = set()
                prop4.add((("P", adjTiles[0]), False))
                prop4.add((("P", adjTiles[1]), False))
                prop4.add((("P", adjTiles[2]), False))
                self.kb.tell(MazeClause(prop4))
                    
            elif counter == 4:
                print("Too unreasonable to write out all of proposition logic")
                # Same reason as the "tile" = 1
                
            self.safe_tiles.add(perception['loc'])
            self.add_Pit(perception["loc"], False)
            self.kb.simplify_self(self.pit_tiles, self.safe_tiles)
        elif perception["tile"] == "3":
            for adjacentLocation in self.env.get_cardinal_locs(perception['loc'], 1):
                if adjacentLocation not in self.visited_tiles or adjacentLocation not in self.safe_tiles or len(self.visited_tiles) == 0:
                    self.pit_tiles.add(adjacentLocation)
                    self.add_Pit(adjacentLocation, True)
                    
            self.safe_tiles.add(perception['loc'])
            self.add_Pit(perception["loc"], False)
            self.kb.simplify_self(self.pit_tiles, self.safe_tiles)
        elif perception["tile"] == "4":
            print("wtf whyd u give me 4 pits im gonna unalive myself")
            for adjacentLocation in self.env.get_cardinal_locs(perception['loc'], 1):
                self.pit_tiles.add(adjacentLocation)
                self.add_Pit(adjacentLocation, True)
                
            self.safe_tiles.add(perception['loc'])
            self.add_Pit(perception["loc"], False)
        elif perception["tile"] == "P":
            self.pit_tiles.add(perception["loc"])
            self.add_Pit(perception["loc"], True)
        elif perception['tile'] == ".":
            #We know the tile we are on is not a pt
            self.safe_tiles.add(perception["loc"])
            self.add_Pit(perception["loc"], False)
            
            #We also know the tile surrounding this tile are not pits because there was not warning
            for adjacentLocation in self.env.get_cardinal_locs(perception['loc'], 1):
                self.safe_tiles.add(adjacentLocation)
                self.add_Pit(adjacentLocation, False)
        
        elif perception['tile'] == "0":
            print("How tf did this happen")
            #Same code as if tile was "."
            self.safe_tiles.add(perception["loc"])
            self.add_Pit(perception["loc"], False)
            
            for adjacentLocation in self.env.get_cardinal_locs(perception['loc'], 1):
                self.safe_tiles.add(adjacentLocation)
                self.add_Pit(adjacentLocation, False)
        
        self.visited_tiles.add(perception["loc"])
        
        if self.env.get_goal_loc() in frontier:
            return self.env.get_goal_loc()
        
        safeLocs: set[tuple[int, int]] = set()
        unsafeLocs: set[tuple[int, int]] = set()
        for loc in frontier:
            if loc not in self.visited_tiles:
                if loc not in self.safe_tiles:
                    x = self.is_safe_tile(loc)
                    if x == True:
                        safeLocs.add(loc)
                        self.safe_tiles.add(loc)
                        self.add_Pit(loc, False)
                    elif x == False:
                        if loc not in self.pit_tiles:
                            self.pit_tiles.add(loc)
                    else:
                        unsafeLocs.add(loc)
                elif loc in self.safe_tiles:
                    safeLocs.add(loc)
        
        
        # print(" After think operation: ")
        # print("     possible_pits after:")
        # for tile in self.possible_pits:
        #     print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        # print("     safe_tiles after:")
        # for tile in self.safe_tiles:
        #     print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        # print("     pit_tiles after:")
        # for tile in self.pit_tiles:
        #     print("     [" + str(tile[0]) + ", " + str(tile[1]) + "]", end = "   ")
        # print("\n")
        
        return self.get_best_tile(safeLocs, unsafeLocs)

    def add_Pit (self, loc: tuple[int, int], boo: bool):
        # Adds KNOWN pit/safe locations to kb
        tileSet = set()
        tileSet.add((("P", loc), boo))
        
        if loc in self.possible_pits:
            self.possible_pits.remove(loc)
        
        self.kb.tell(MazeClause(tileSet))
        self.kb.simplify_self(self.pit_tiles, self.safe_tiles)
        
    def get_best_tile (self, safe: set[tuple[int, int]], unsafe: set[tuple[int, int]]) -> tuple[int, int]:
        # Make better heuristic based on cost because moving multple tiles at once costs alot so reduce cost also try optimizing pls
        bestTile = tuple[int, int]
        lowestCost = float('inf')
        goal = self.env.get_goal_loc()
        for loc in safe:
            xDistance = abs(goal[0] - loc[0])
            yDistance = abs(goal[1] - loc[1])
            if xDistance + yDistance < lowestCost:
                lowestCost = xDistance + yDistance
                bestTile = loc
        for loc in unsafe:
            xDistance = abs(goal[0] - loc[0])
            yDistance = abs(goal[1] - loc[1])
            if xDistance + yDistance + 2 < lowestCost:
                lowestCost = xDistance + yDistance + 4
                bestTile = loc
        
        return bestTile
        
    def is_safe_tile (self, loc: tuple[int, int]) -> Optional[bool]:
        """
        Determines whether or not the given maze location can be concluded as
        safe (i.e., not containing a pit), following the steps:
        1. Check to see if the location is already a known pit or safe tile,
           responding accordingly
        2. If not, performs the necessary queries on the knowledge base in an
           attempt to deduce its safety
        
        Parameters:
            loc (tuple[int, int]):
                The maze location in question
        
        Returns:
            One of three return values:
            1. True if the location is certainly safe (i.e., not pit)
            2. False if the location is certainly dangerous (i.e., pit)
            3. None if the safety of the location cannot be currently determined
        """
        
        #Lets assume loc is not a pit
        prop1 = set()
        prop1.add((("P", loc), False))
        clause1 = MazeClause(prop1)
        
        if self.kb.ask(clause1) == True:
            #False because KB entails prop if its a pit
            return True
        
        #Now we do opposite
        prop2 = set()
        prop2.add((("P", loc), True))
        clause2 = MazeClause(prop2)
        
        if self.kb.ask(clause2) == True:
            #False because KB entails prop if its a pit
            return False
        
        #if both fails return None
        return None
        
    
    def is_adjacent_tile (self, loc: tuple[int, int], loc2: tuple[int, int]) -> bool:
        if loc == loc2:
            return False
        return (loc[0] == loc2[0] or abs(loc[0] - loc2[0]) == 1) and (loc[1] == loc2[1] or abs(loc[1] - loc2[1]) == 1)
    
    
            

# Declared here to avoid circular dependency
from environment import Environment