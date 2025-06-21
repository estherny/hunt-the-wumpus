
class GameTile:

	def __init__(self, tile_type=2, discovered=False, game_tile=None):
		if game_tile is None:
			self.tile_type = tile_type

			self.discovered = discovered
			self.has_pit = False
			self.has_wumpus = False
			self.has_glitter = False
			self.has_breeze = False
			self.has_stench = False
			self.has_player = False
			self.heard_scream = False
		else:
			self.discovered = game_tile.discovered
			self.tile_type = game_tile.tile_type

			self.has_pit = game_tile.has_pit
			self.has_wumpus = game_tile.has_wumpus
			self.has_glitter = game_tile.has_glitter
			self.has_breeze = game_tile.has_breeze
			self.has_stench = game_tile.has_stench
			self.has_player = game_tile.has_player
			self.heard_scream = game_tile.heard_scream

	def is_ground(self):
		return self.tile_type == GameTile.IS_GROUND

	def is_wall(self):
		return self.tile_type == GameTile.IS_WALL

	def __str__(self):
		s = ""
		if self.tile_type == GameTile.IS_GROUND:
			s += " "
		elif self.tile_type == GameTile.IS_WALL:
			s += "#"
		elif self.tile_type == GameTile.IS_UNKNOWN:
			s += "U"
		else:
			print("Unknown tile type " + self.tile_type)

		if self.has_player:
			s += "P"
		if self.has_stench:
			s += "S"
		if self.has_breeze:
			s += "B"
		if self.has_glitter:
			s += "G"
		if self.has_wumpus:
			s += "U"
		if self.has_pit:
			s += "H"
		if self.heard_scream:
			s += "D"
		return s + " "

GameTile.IS_GROUND = 0
GameTile.IS_WALL = 1
GameTile.IS_UNKNOWN = 2
