from collections import deque
from AgentAction import AgentAction
from Variables import Variables
import random

class AgentBrain:
    def __init__(self):
        self.current_num_moves = 0
        self.previous_moves = deque()
        self._next_move = None

    @property
    def next_move(self):
        return self._next_move

    @next_move.setter
    def next_move(self, m):
        if m == AgentAction.quit:
            exit(0)
        elif self._next_move is not None:
            print("Trouble adding move, only allowed to add 1 at a time")
        else:
            self._next_move = m

    def get_opposite_action(self, a: AgentAction):
        if a == AgentAction.move_down:
            return AgentAction.move_up
        elif a == AgentAction.move_up:
            return AgentAction.move_down
        elif a == AgentAction.move_left:
            return AgentAction.move_right
        elif a == AgentAction.move_right:
            return AgentAction.move_left
        return AgentAction.do_nothing

    # Function to assign the player to a random location
    def assign_random_player_location(self, map):
        rows = len(map)
        cols = len(map[0])
        random_row = random.randint(0, rows - 1)
        random_col = random.randint(0, cols - 1)
        return random_row, random_col

    # Check if the move is valid (within bounds of the map)
    @staticmethod
    def is_valid_move(row, col, map):
        rows = len(map)
        cols = len(map[0])
        valid = 0 <= row < rows and 0 <= col < cols
        if not valid:
            print(f"Invalid move: Out of bounds ({row}, {col})")
        return valid

    # Function to make the entire map visible
    def make_all_visible(self, map):
        for row in map:
            for tile in row:
                tile.is_visible = True

    # Function to check for Wumpus, pits, or walls (if present)
    @staticmethod
    def safe_move(row, col, map):
        if map[row][col].has_wumpus:
            print(f"Move to ({row}, {col}) is unsafe due to Wumpus!")
            return False
        if map[row][col].has_pit:
            print(f"Move to ({row}, {col}) is unsafe due to Pit!")
            return False
        if map[row][col].is_wall():
            print(f"Move to ({row}, {col}) is unsafe due to Wall!")
            return False
        return True

    def random_move(self, visible_map):
        row, col = self.get_player_position(visible_map)
        moves = deque()

        if col > 0 and self.is_valid_move(row, col - 1, visible_map) and self.safe_move(row, col - 1, visible_map):
            moves.append(AgentAction.move_left)
        if row < len(visible_map) - 1 and self.is_valid_move(row + 1, col, visible_map) and self.safe_move(row + 1, col, visible_map):
            moves.append(AgentAction.move_down)
        if row > 0 and self.is_valid_move(row - 1, col, visible_map) and self.safe_move(row - 1, col, visible_map):
            moves.append(AgentAction.move_up)
        if col < len(visible_map[0]) - 1 and self.is_valid_move(row, col + 1, visible_map) and self.safe_move(row, col + 1, visible_map):
            moves.append(AgentAction.move_right)

        if len(moves) == 0:
            print("No valid moves available!")
            return AgentAction.declare_victory

        chosen_move = random.choice(moves)
        return chosen_move

    @staticmethod
    def get_player_position(map):
        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j].has_player:
                    return i, j
        return None, None

    def get_next_move(self, visible_map):
        if Variables.GAME_PLAY_TYPE == Variables.GamePlayType.KEYBOARD:
            if self._next_move is None:
                return AgentAction.do_nothing
            else:
                tmp = self._next_move
                self._next_move = None
                return tmp

        elif Variables.GAME_PLAY_TYPE == Variables.GamePlayType.RANDOM:
            if Variables.RANDOMIZE_PLAYER:
                if self.current_num_moves < Variables.NUM_RANDOM_MOVES:
                    self.current_num_moves += 1
                    return self.random_move(visible_map)
                return AgentAction.declare_victory

        else:
            return self.brain(visible_map)

    @staticmethod
    def brain(visible_map):
        return AgentBrain.get_out_alive(visible_map)

    @staticmethod
    def get_out_alive(visible_map):
        player_row, player_col = AgentBrain.get_player_position(visible_map)

        if player_row is not None and player_col is not None:
            if player_row == 4 and player_col == 1:
                return AgentAction.declare_victory

            if AgentBrain.is_valid_move(player_row, player_col - 1, visible_map) and AgentBrain.safe_move(player_row, player_col - 1, visible_map):
                return AgentAction.move_left
            if AgentBrain.is_valid_move(player_row + 1, player_col, visible_map) and AgentBrain.safe_move(player_row + 1, player_col, visible_map):
                return AgentAction.move_down
            if AgentBrain.is_valid_move(player_row - 1, player_col, visible_map) and AgentBrain.safe_move(player_row - 1, player_col, visible_map):
                return AgentAction.move_up
            if AgentBrain.is_valid_move(player_row, player_col + 1, visible_map) and AgentBrain.safe_move(player_row, player_col + 1, visible_map):
                return AgentAction.move_right

        print("No valid move available")
        return AgentAction.declare_victory

    def find_wumpus(self, visible_map):
        for i in range(len(visible_map)):
            for j in range(len(visible_map[i])):
                if visible_map[i][j].has_wumpus:
                    return (i, j)
        return None

    def get_neighbors(self, pos, visible_map):
        row, col = pos
        directions = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        return [(r, c) for r, c in directions if self.is_valid_move(r, c, visible_map)]

    def navigate_to_shoot_wumpus(self, visible_map):
        player_pos = self.get_player_position(visible_map)
        wumpus_pos = self.find_wumpus(visible_map)

        if not wumpus_pos:
            print("No Wumpus found!")
            return AgentAction.declare_victory

        neighbors = self.get_neighbors(wumpus_pos, visible_map)
        valid_positions = [pos for pos in neighbors if self.safe_move(*pos, visible_map)]

        if not valid_positions:
            print("No safe position to shoot the Wumpus.")
            return AgentAction.declare_victory

        target_pos = random.choice(valid_positions)
        return self.find_path(player_pos, target_pos, visible_map)

    def find_path(self, start, goal, map):
    #Finds the shortest path from `start` to `goal` on the map using BFS.Returns the next move to get closer to the goal.
        from collections import deque

    # Directions: (row_offset, col_offset, corresponding action)
        directions = [
            (-1, 0, AgentAction.move_up),
            (1, 0, AgentAction.move_down),
            (0, -1, AgentAction.move_left),
            (0, 1, AgentAction.move_right),
        ]

    # BFS queue: stores (current_position, path_to_here)
        queue = deque([(start, [])])
        visited = set()
        visited.add(start)

        while queue:
            current_pos, path = queue.popleft()
            row, col = current_pos

            # Goal reached
            if current_pos == goal:
                if path:  # Return the first move in the path
                    return path[0]
                return AgentAction.declare_victory

        # Explore neighbors
            for dr, dc, action in directions:
                new_row, new_col = row + dr, col + dc
                new_pos = (new_row, new_col)

                if (
                    self.is_valid_move(new_row, new_col, map)  # Within map bounds
                    and self.safe_move(new_row, new_col, map)  # Avoid hazards
                    and new_pos not in visited  # Not visited yet
                ):
                    queue.append((new_pos, path + [action]))
                    visited.add(new_pos)

        # If no path is found
        print("No valid path found from start to goal!")
        return AgentAction.declare_victory