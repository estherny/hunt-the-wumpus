from collections import deque
from GameTile import GameTile
import random

class AgentAction:
	def __init__(self, is_an_action: bool):
		self.is_an_action = is_an_action
	
	def __str__(self):
		if self == AgentAction.move_left:
			return "Move Left"
		elif self == AgentAction.move_right:
			return "Move Right"
		elif self == AgentAction.move_up:
			return "Move Up"
		elif self == AgentAction.move_down:
			return "Move Down"
		elif self == AgentAction.pickup_something:
			return "Pickup Something"
		elif self == AgentAction.declare_victory:
			return "Declare Victory"
		elif self == AgentAction.do_nothing:
			return "Do Nothing"
		elif self == AgentAction.shoot_arrow_north:
			return "Shoot Arrow North"
		elif self == AgentAction.shoot_arrow_south:
			return "Shoot Arrow South"
		elif self == AgentAction.shoot_arrow_east:
			return "Shoot Arrow East"
		elif self == AgentAction.shoot_arrow_west:
			return "Shoot Arrow West"
		return "Unknown Action"

	@staticmethod
	def removeBackAndForth(a):
		size = len(a)+1
		while len(a) < size:
			size = len(a)
			newMoves = deque()
			for i in range(len(a)):
				if i == len(a)-1:
					newMoves.append(a[i])
				elif a[i] == AgentAction.move_down and a[i+1] == AgentAction.move_up:
					i += 1 #skip both
				elif a[i] == AgentAction.move_up and a[i+1] == AgentAction.move_down:
					i += 1 #skip both
				elif a[i] == AgentAction.move_left and a[i+1] == AgentAction.move_right:
					i += 1 #skip both
				elif a[i] == AgentAction.move_right and a[i+1] == AgentAction.move_left:
					i += 1 #skip both
				else:
					newMoves.append(a[i])
			a = newMoves
		return a

	@staticmethod
	def randomAction(map):
		row = -1
		col = -1
		
		stop = False
		for i in range(len(map)):
			for j in range(len(map[i])):
				if map[i][j] is not None and map[i][j].has_player:
					row = i
					col = j
					if(map[row][col].has_glitter):
						return AgentAction.pickup_something
					else:
						stop = True
						break
			if(stop):
				break
		
		moves = deque()
		if row > 1:
			if map[row-1][col] == None:
				if not(map[row][col].has_breeze or map[row][col].has_stench):
					moves.append(AgentAction.move_up)
			else:
				if not map[row-1][col].has_wumpus and not map[row-1][col].has_pit:
					moves.append(AgentAction.move_up)
		if row < 4:
			if map[row+1][col] == None:
				if not(map[row][col].has_breeze or map[row][col].has_stench):
					moves.append(AgentAction.move_down)
			else:
				if not map[row+1][col].has_wumpus and not map[row+1][col].has_pit:
					moves.append(AgentAction.move_down)
		if col > 1:
			if map[row][col-1] == None:
				if not(map[row][col].has_breeze or map[row][col].has_stench):
					moves.append(AgentAction.move_left)
			else:
				if not map[row][col-1].has_wumpus and not map[row][col-1].has_pit:
					moves.append(AgentAction.move_left)
		if col < 4:
			if map[row][col+1] == None:
				if not(map[row][col].has_breeze or map[row][col].has_stench):
					moves.append(AgentAction.move_right)
			else:
				if not map[row][col+1].has_wumpus and not map[row][col+1].has_pit:
					moves.append(AgentAction.move_right)
		
		if len(moves) == 0:
			return AgentAction.declare_victory
		return moves[random.randint(0,len(moves)-1)]

AgentAction.move_left = AgentAction(True)
AgentAction.move_right = AgentAction(True)
AgentAction.move_up = AgentAction(True)
AgentAction.move_down = AgentAction(True)

AgentAction.pickup_something = AgentAction(True)
AgentAction.declare_victory = AgentAction(False)

AgentAction.do_nothing = AgentAction(False)


AgentAction.shoot_arrow_north = AgentAction(True)
AgentAction.shoot_arrow_south = AgentAction(True)
AgentAction.shoot_arrow_east = AgentAction(True)
AgentAction.shoot_arrow_west = AgentAction(True)

AgentAction.quit = AgentAction(False)
