from GameTile import GameTile
from AgentAction import AgentAction
from AgentBrain import AgentBrain
from collections import deque
from Variables import Variables
import random

class GameInstance:

	def __init__(self, rows=0,cols=0,map=None, screen_instance=None):

		self.num_actions = 0
		self.player_declares_victory = False
		self.quit = False
		self.picked_up_gold = False
		self.met_death = False
		self.results_printed = False
		self.move_to_next_round = False

		self.player_x = 1
		self.player_y = 1

		self.brain = None

		self.points = 0
		self.has_arrow = True
		self.gui = screen_instance

		if(not map):
			rows+=2; #Pad it with walls around the outside
			cols+=2; #Pad it with walls around the outside

			self.full_map = []
			self.visible_map = []
			for i in range(rows):
				self.full_map.append([])
				self.visible_map.append([])
				for j in range(cols): 
					self.full_map[i].append(None)
					self.visible_map[i].append(None)
			self.make_random_world()

		else:
			self.rows = len(map)
			self.cols = len(map[0])
			self.full_map = []
			self.visible_map = []
			for i in range(0,self.rows):
				self.full_map.append([])
				self.visible_map.append([])
				for j in range(0, self.cols): 
					self.full_map[i].append(GameTile(game_tile=map[i][j]))
					self.visible_map[i].append(None)
			self.reset_variables()
			print(GameInstance.get_string_representation(self.full_map,False))
		
	def get_full_map(self):
		if self.full_map == None:
			return None
		new_map = []
		for i in range(len(self.full_map)):
			new_map.append([])
			for j in range(len(self.full_map[i])):
				new_map[i].append(GameTile(game_tile=self.full_map[i][j]))
		return new_map
	
	def advance_time(self):
		if self.player_declares_victory:
			if not self.results_printed:
				self.results_printed = True
				print("This round: ")
				self.points -= self.num_actions
				print("\tTotal Actions:", self.num_actions)
				if self.player_x == len(self.full_map)-2 and self.player_y == 1:
					if self.picked_up_gold:
						self.points += 1000
						print("\tFound gold +1000")
					else:
						print("\tMade it out alive! But without the gold :(")
				else:
					self.points -= 1000
					if self.met_death:
						print("\tDied from pit or wumpus -1000")
					else:
						print("\tGot lost in dark -1000")
				if not self.has_arrow:
					self.points -= 10
					print("\tShot arrow -10")
				print(self.points, "Current point total ")
			if self.move_to_next_round:
				self.make_random_world()
		else:
			self.move()
	
	def reset_variables(self):
		if self.gui != None:
			self.gui.setup_pictures()
		self.has_arrow = True
		self.picked_up_gold = False
		self.met_death = False
		
		self.results_printed = False
		self.move_to_next_round = False

		if Variables.AUTO_ADVANCE_ROUNDS:
			self.move_to_next_round = True

		self.num_actions = 0
		self.player_declares_victory = False

		self.brain = AgentBrain()
		Variables.num_games_played+=1
		if Variables.num_games_played > Variables.NUM_GAMES:
			exit(0)

		self.player_x = len(self.full_map)-2
		self.player_y = 1
		if Variables.RANDOMIZE_PLAYER:
			self.player_x = random.randint(1,len(self.full_map)-2)
			self.player_y = random.randint(1,len(self.full_map)-2)

		self.full_map[self.player_x][self.player_y].has_player = True
		self.make_things_visable_at_this_location(self.player_x,self.player_y)

		if Variables.REMOVE_DARKNESS:
			for i in range(0,len(self.full_map)):
				for j in range(0,len(self.full_map[i])):
					self.make_things_visable_at_this_location(i,j)
	
	def game_is_over(self):
		return self.player_declares_victory
	
	def make_random_world(self):
		
		rows = len(self.full_map)
		cols = len(self.full_map[0])
		for i in range(0,rows):
			for j in range (0,cols):
				self.full_map[i][j] = GameTile(GameTile.IS_GROUND, discovered=False)
				self.visible_map[i][j] = None

		#Add the walls to the outside of the map
		for i in range(0,rows):
			self.full_map[i][0] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			self.full_map[i][cols-1] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			self.visible_map[i][0] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			self.visible_map[i][cols-1] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
		for i in range(0,cols):
			self.full_map[0][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			self.full_map[rows-1][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			self.visible_map[0][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			self.visible_map[rows-1][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)

		if Variables.ADD_PITS:
			#Add pits, and the breeze around them
			num_pits = random.randint(1,3)
			for i in range(0,num_pits):
				found = False
				while not found:
					x = random.randint(1,len(self.full_map)-1)
					y = random.randint(1,len(self.full_map[0])-1)
					if x == len(self.full_map)-2 and y == 1:
						# Don't add to where player starts
						pass
					elif self.full_map[x][y].is_ground():
						self.add_pit(x,y,self.full_map)
						found = True
		#Add wumpus and stench
		if Variables.ADD_WUMPUS:
			found = False
			while not found:
				x = random.randint(1,len(self.full_map)-1)
				y = random.randint(1,len(self.full_map[0])-1)
				if x == len(self.full_map)-2 and y == 1:
					# Don't add to where player starts
					pass
				elif self.full_map[x][y].is_ground():
					#Don't need to remember breeze, because -1000
					self.add_wumpus(x,y,self.full_map)
					if Variables.MAKE_WUMPUS_GUARD_GOLD:
						self.full_map[x][y].has_glitter = True
					found = True
				elif(self.full_map[x][y].has_pit or self.full_map[x][y].is_wall()):
					#Don't add it
					pass
				else:
					print("Unhandled case when adding wumpus:", self.full_map[x][y].get_tile_type())


		#Add Walls to inside of map
		if Variables.ADD_WALLS:
			num_walls = random.randint(0,rows-3)
			for i in range(0, num_walls):
				found = False
				while not found:
					x = random.randint(1,len(self.full_map)-1)
					y = random.randint(1,len(self.full_map[0])-1)
					if x == len(self.full_map)-2 and y == 1:
						# Don't add to where player starts
						pass
					elif self.full_map[x][y].is_ground() and not self.full_map[x][y].has_glitter and not self.full_map[x][y].has_wumpus:
							self.full_map[x][y] = GameTile(tile_type=GameTile.IS_WALL, discovered=False)
							found = True

		#Add gold
		if not Variables.MAKE_WUMPUS_GUARD_GOLD:
			found = False
			while not found:
				x = random.randint(1,len(self.full_map)-1)
				y = random.randint(1,len(self.full_map[0])-1)
				if x == len(self.full_map)-2 and y == 1:
					# Don't add to where player starts
					pass
				elif self.full_map[x][y].is_wall() or self.full_map[x][y].has_pit:
					#Don't add it
					pass
				elif self.full_map[x][y].is_ground():
					self.full_map[x][y].has_glitter = True
					found = True
				else:
					print("Unhandled case when adding gold", self.full_map[x][y].get_tile_type())
		self.reset_variables()

	def set_next_move(self, keyevent):
		keychar = keyevent.char
		if(keychar == ""):
			keychar = keyevent.keysym

		up = ["w","W","Up"]
		down = ["s", "S", "Down"]
		left = ["a","A","Left"]
		right = ["d","D", "Right"]
		victory = ["v","V"]
		pickup = [" "]
		quit = ["q","Q"]
		shoot_north = ["i","I"]
		shoot_south = ["k","K"]
		shoot_east = ["l","L"]
		shoot_west = ["j","J"]
		cheat = ["c","C"]
		next = ["n","N"]

		if keychar in right:
			self.brain.next_move = AgentAction.move_right
		elif keychar in left:
			self.brain.next_move = AgentAction.move_left
		elif keychar in up:
			self.brain.next_move = AgentAction.move_up
		elif keychar in down:
			self.brain.next_move = AgentAction.move_down
		elif keychar in victory:
			self.brain.next_move = AgentAction.declare_victory
		elif keychar in pickup:
			self.brain.next_move = AgentAction.pickup_something
		elif keychar in quit:
			self.brain.next_move = AgentAction.quit
		elif keychar in shoot_north:
			self.brain.next_move = AgentAction.shoot_arrow_north
		elif keychar in shoot_south:
			self.brain.next_move = AgentAction.shoot_arrow_south
		elif keychar in shoot_east:
			self.brain.next_move = AgentAction.shoot_arrow_east
		elif keychar in shoot_west:
			self.brain.next_move = AgentAction.shoot_arrow_west
		elif keychar in cheat:
			Variables.CHEATMODE_ON = not Variables.CHEATMODE_ON
		elif keychar in next:
			GameInstance.move_to_next_round = True
		else:
			print("Unknown key event " + str(keyevent))

	def make_things_visable_at_this_location(self, x, y):
		self.visible_map[x][y] = self.full_map[x][y]
		self.visible_map[x][y].discovered = True


	def is_valid_move(self, newRow, newCol):
		if  0 <= newRow and 0 <= newCol and newRow < len(self.full_map) and newCol < len(self.full_map[0]):
			#print("In bounds")
			self.make_things_visable_at_this_location(newRow, newCol)
			if self.full_map[newRow][newCol].is_ground():
				return True
			else:
				return False
		else:
			print("Out of bounds")
		return False

	def move(self):
		temp_map = []
		for i in range(len(self.visible_map)):
			temp_map.append([])
			for j in range(len(self.visible_map[i])):
				if self.visible_map[i][j] != None:
					temp_map[i].append(GameTile(game_tile=self.visible_map[i][j]))
				else:
					temp_map[i].append(None)

		action = self.brain.get_next_move(temp_map)
		if action == None:
			return

		row = self.player_x
		col = self.player_y

		self.last_action_worked = True
		if action == AgentAction.declare_victory:
			self.player_declares_victory = True
		elif action == AgentAction.quit:
			self.player_declares_victory = True
			self.quit = True
		elif action == AgentAction.pickup_something:
			self.last_action_worked = False
			if self.full_map[row][col].has_glitter:
				self.last_action_worked = True
				self.picked_up_gold = True
				self.full_map[row][col].has_glitter = False

		elif action == AgentAction.move_right:
			self.make_things_visable_at_this_location(row,col+1)
			if self.is_valid_move(row,col+1):
				self.full_map[row][col].has_player = False
				self.full_map[row][col+1].has_player = True
				self.visible_map[row][col] = self.full_map[row][col]
				self.visible_map[row][col+1] = self.full_map[row][col+1]
				self.player_y+=1
			else:
				self.last_action_worked = False

		elif action == AgentAction.move_left:
			self.make_things_visable_at_this_location(row,col-1)
			if self.is_valid_move(row,col-1):
				self.full_map[row][col].has_player = False
				self.full_map[row][col-1].has_player = True
				self.visible_map[row][col] = self.full_map[row][col]
				self.visible_map[row][col-1] = self.full_map[row][col-1]
				self.player_y-=1
			else:
				self.last_action_worked = False

		elif action == AgentAction.move_up:
			self.make_things_visable_at_this_location(row-1,col)
			if self.is_valid_move(row-1,col):
				self.full_map[row][col].has_player = False
				self.full_map[row-1][col].has_player = True
				self.visible_map[row][col] = self.full_map[row][col]
				self.visible_map[row-1][col] = self.full_map[row-1][col]
				self.player_x-=1
			else:
				self.last_action_worked = False
		elif action == AgentAction.move_down:
			self.make_things_visable_at_this_location(row+1,col)
			if self.is_valid_move(row+1,col):
				self.full_map[row][col].has_player = False
				self.full_map[row+1][col].has_player = True
				self.visible_map[row][col] = self.full_map[row][col];
				self.visible_map[row+1][col] = self.full_map[row+1][col];
				self.player_x+=1
			else:
				self.last_action_worked = False
		elif action == AgentAction.shoot_arrow_north:
			self.shoot_arrow(AgentAction.shoot_arrow_north)
		elif action == AgentAction.shoot_arrow_south:
			self.shoot_arrow(AgentAction.shoot_arrow_south)
		elif action == AgentAction.shoot_arrow_east:
			self.shoot_arrow(AgentAction.shoot_arrow_east)
		elif action == AgentAction.shoot_arrow_west:
			self.shoot_arrow(AgentAction.shoot_arrow_west)
		elif action == AgentAction.do_nothing:
			pass
		else:
			print("Unhandled action", action)

		if action.is_an_action:
			self.num_actions+=1
			if self.full_map[self.player_x][self.player_y].has_pit:
				print("Player met an untimely death by pit")
				self.met_death = True
				self.player_declares_victory = True
			if self.full_map[self.player_x][self.player_y].has_wumpus:
				print("Player met an untimely death by wumpus")
				self.met_death = True
				self.player_declares_victory = True

	def shoot_arrow(self, a:AgentAction):
		#Only shoot if there is an arrow
		if not self.has_arrow:
			print("\tNo more arrows")
			return
		self.has_arrow = False

		x = 0
		y = 0
		found_player = False
		i = 0
		while i < len(self.full_map) and not found_player:
			j = 0
			while j < len(self.full_map[i]) and not found_player:
				if self.full_map[i][j].has_player:
					found_player = True
					x = i
					y = j
				j += 1
			i+=1
		if found_player:
			#arrow stops at wumpus or wall
			if a == AgentAction.shoot_arrow_north:
				for i in range(x, 0, -1):
					if self.full_map[i][y].has_wumpus:
						self.full_map[i][y].has_wumpus = False
						self.echo_the_scream()
						break
					elif self.full_map[i][y].is_wall():
						return
			elif a == AgentAction.shoot_arrow_south:
				for i in range(x, len(self.full_map)):
					if self.full_map[i][y].has_wumpus:
						self.full_map[i][y].has_wumpus = False
						self.echo_the_scream()
						break
					elif self.full_map[i][y].is_wall():
						return
			elif a == AgentAction.shoot_arrow_east:
				for i in range(y, len(self.full_map[x])):
					if self.full_map[x][i].has_wumpus:
						self.full_map[x][i].has_wumpus = False
						self.echo_the_scream()
						break
					elif self.full_map[x][i].is_wall():
						return
			elif a == AgentAction.shoot_arrow_west:
				for i in range(y, 0, -1):
					if self.full_map[x][i].has_wumpus:
						self.full_map[x][i].has_wumpus = False
						self.echo_the_scream()
						break
					elif self.full_map[x][i].is_wall():
						return

	def echo_the_scream(self):
		print("\tWumpus's woeful death scream echoes through the cave")
		for i in range(len(self.full_map)):
			for j in range(len(self.full_map[i])):
				self.full_map[i][j].heard_scream = True
				if self.visible_map[i][j] != None:
					self.visible_map[i][j].heard_scream = True

	#This method adds a pit to the map, and the associated breeze's
	#Doesn't add a pit if it is on a wall
	@staticmethod
	def add_pit(x, y, map):
		if x < len(map)-1 and y < len(map[0])-1 and x > 0 and y > 0:
			if not map[x][y].is_wall():
				map[x][y].has_pit = True
				GameInstance.add_breeze(x+1,y, map)
				GameInstance.add_breeze(x-1,y, map)
				GameInstance.add_breeze(x,y+1, map)
				GameInstance.add_breeze(x,y-1, map)

	#This method adds the wumpus to the map, and the associated stench
	#Doesn't add a wumpus if it is on a wall, but allow wumpus to be in a pit - as if he fell down it
	@staticmethod
	def add_wumpus(x, y, map):
		if x < len(map)-1 and y < len(map[0])-1 and x > 0 and y > 0:
			if not map[x][y].is_wall():
				map[x][y].has_wumpus = True
				GameInstance.add_stench(x+1,y, map)
				GameInstance.add_stench(x-1,y, map)
				GameInstance.add_stench(x,y+1, map)
				GameInstance.add_stench(x,y-1, map)

	@staticmethod
	def add_breeze(x, y, map):
		if x < len(map)-1 and y < len(map[0])-1 and x > 0 and y > 0:
			if not map[x][y].is_wall():
				map[x][y].has_breeze = True

	@staticmethod
	def add_stench(x, y, map):
		if x < len(map)-1 and y < len(map[0])-1 and x > 0 and y > 0:
			if not map[x][y].is_wall():
				map[x][y].has_stench = True
		
	@staticmethod
	def get_string_representation(map, small:bool):
		s = ""
		startI = 0
		endI = len(map)
		startJ = 0
		endJ = len(map[0])
		if small:
			startI+=1
			endI-=1
			startJ+=1
			endJ-=1
		for i in range(startI, endI):
			for j in range (startJ, endJ):
				if map[i][j].is_wall():
					s += "#"
				elif map[i][j].has_player:
					if map[i][j].has_glitter:
						s += "<"
					else:
						s += "^"
				else:
					items = 0
					if map[i][j].has_wumpus:
						items += 1
					if map[i][j].has_pit:
						items += 10
					if map[i][j].has_glitter:
						items += 100
					if items == 0:
						s+=" "
					elif items == 1:
						s+="W"
					elif items == 10:
						s+="P" #Pit
					elif items == 11:
						s+="S" #Wumpus & Pit
					elif items == 100:
						s+="G"
					elif items == 101:
						s+="K" #wumpus and gold
					elif items == 110:
						s+="O" #Gold and Pit
					elif items == 111:
						s+="3" #Gold, Pit, Wumpus
					else :
						s += "?"
			s += "\n"		
		return s
		
	@staticmethod
	def generate_maps_with_1_wall_and_2_pits(rows, cols):
		most_maps = deque()
		blank_map = []
		
		no_dups = {}

		for i in range(rows):
			blank_map.append([])
			for j in range(cols):
				blank_map[i].append(GameTile(tile_type=GameTile.IS_GROUND, discovered=False))

		#Add the walls to the outside of the map
		for i in range(rows):
			blank_map[i][0] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			blank_map[i][cols-1] =  GameTile(tile_type=GameTile.IS_WALL, discovered=True)

		for i in range(cols):
			blank_map[0][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			blank_map[rows-1][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)

		player_x = len(blank_map)-2
		player_y = 1
		blank_map[player_x][player_y].has_player = True

		#We need all combinations of pits/walls/gold
		#Player always bottom left - no gold, no pit
		num_maps = 0
		rows -= 2
		cols -= 2
		size = rows*cols
		for i in range(size): #Pit
			print("i", i,"num_maps", num_maps)
			for j in range(size+1): #Pit
				for l in range(size): #Wall
					if i == l or j == l:
						continue
					for o in range(size): #Wumpus - can be on pit
						if l == o: #not on a wall
							continue
						for p in range(size): #Gold - can be on pit and wumpus
							if l == p: #not on a wall
								continue
							map = []
							for q in range(len(blank_map)):
								map.append([])
								for r in range(len(blank_map[q])):
									map[q].append(GameTile(game_tile=blank_map[q][r]))

							#12 is player
							if i != 12:
								GameInstance.add_pit(i//4+1,i%4+1,map)
							if j != 12 and j < 16:
								GameInstance.add_pit(j//4+1,j%4+1,map)
							if l != 12:
								map[l//4+1][l%4+1] = GameTile(tile_type=GameTile.IS_WALL, discovered=False)
							if o != 12:
								GameInstance.add_wumpus(o//4+1,o%4+1,map)
							if p != 12:
								map[p//4+1][p%4+1].has_glitter = True

							s = GameInstance.get_string_representation(map, True)
							if s in no_dups:
								# print("Map already exists")
								# print("'")
								# print(s)
								# print("'")
								# print("i", i,"numMaps", numMaps)
								# raise IndexError()
								pass
							else:
								# print(s)
								num_maps+=1
								no_dups[s] = True
								most_maps.append(map)
		
		print("Maps created", num_maps)
		return most_maps
		
	@staticmethod
	def generate_maps_with_2_walls_and_2_pits(rows, cols):
		most_maps = deque()
		blank_map = []
		
		noDups = {}

		for i in range(rows):
			blank_map.append([])
			for j in range(cols):
				blank_map[i].append(GameTile(tile_type=GameTile.IS_GROUND, discovered=False))

		#Add the walls to the outside of the map
		for i in range(rows):
			blank_map[i][0] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			blank_map[i][cols-1] =  GameTile(tile_type=GameTile.IS_WALL, discovered=True)

		for i in range(cols):
			blank_map[0][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)
			blank_map[rows-1][i] = GameTile(tile_type=GameTile.IS_WALL, discovered=True)

		player_x = blank_map.length-2
		player_y = 1
		blank_map[player_x][player_y].has_player = True


		#We need all combinations of pits/walls/gold
		#Player always bottom left - no gold, no pit
		num_maps = 0
		rows -= 2
		cols -= 2
		size = rows*cols
		for i in range(size): #Pit
			print("i", i, "num_maps",num_maps)
			for j in range(size+1): #Pit
				for l in range(size): #Wall
					if i == l or j == l:
						continue
					for m in range(l+1, size+1): #Wall
						if i == m or j == m:
							continue
						for o in range(size): #Wumpus - can be on pit
							if l == o or m == o:
								continue
							for p in range(size): #Gold - can be on pit and wumpus
								if l == p or m == p:
									continue
								map = []
								for q in range(len (blank_map)):
									map.append([])
									for r in range(len(blank_map[q])):
										map[q].append(GameTile(game_tile=blank_map[q][r]))
										
								#12 is player

								if i != 12:
									GameInstance.add_pit(i//4+1,i%4+1,map)
								if j != 12 and j < 16:
									GameInstance.add_pit(j//4+1,j%4+1,map)
								if l != 12:
									map[l//4+1][l%4+1] = GameTile(tile_type=GameTile.IS_WALL, discovered=False)
								if m != 12 and m < 16:
									map[m//4+1][m%4+1] = GameTile(tile_type=GameTile.IS_WALL, discovered=False)
								if o != 12:
									GameInstance.add_wumpus(o//4+1,o%4+1,map)
								if p != 12:
									map[p//4+1][p%4+1].has_glitter = True

								s = GameInstance.get_string_representation(map, True)
							if s in noDups:
								print("Map already exists")
								exit(0)
							else:
								num_maps+=1
								noDups[s] = True
								most_maps.append(map)

		print("All Maps", num_maps)
		return most_maps


