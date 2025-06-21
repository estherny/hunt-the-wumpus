import tkinter as tk
from pathlib import Path
import random
from GameInstance import GameInstance
from GameTile import GameTile
from Variables import Variables

class ScreenInstance(tk.Canvas):
	
	def __init__(self, x, y):
		super(ScreenInstance, self).__init__()
		ScreenInstance.setup_pictures()

		self.game_instance = GameInstance(rows=x,cols=y, screen_instance=self)
		self.full_map = self.game_instance.get_full_map()
		self.width = Variables.tile_size*(x+2)
		self.height = Variables.tile_size*(y+2)

		print("Key Listener")
		print("\tawsd or arrows to move")
		print("\tijkl to shoot arrow")
		print("\tspacebar to pickup gold")
		print("\tv to declare victory")
		print("\tc to cheat")
		print("\tn to move onto next round (if applicable)n")
		print("\tq to quit")
		self.pack(fill="both", expand=True)

		self.paint()

	def paint(self):
		self.game_instance.advance_time()
		
		fullMap = self.game_instance.get_full_map()
		if fullMap != None:
			for i in range(0,len(fullMap)):
				for j in range(0, len(fullMap[i])):
					self.draw_the_image(fullMap[i][j], j*Variables.tile_size, i*Variables.tile_size) #Drawing is by col, then row

		self.after(Variables.SLEEP_TIME,self.paint)
	
	def draw_the_image(self, tile, col_on_graphics, row_on_graphics):

		if not tile.discovered and Variables.CHEATMODE_ON == False:
			self.create_image(col_on_graphics, row_on_graphics,image=ScreenInstance.unknown, anchor=tk.NW)
		else:
			if tile.tile_type == GameTile.IS_GROUND:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.ground, anchor=tk.NW)
			elif tile.tile_type == tile.IS_WALL:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.wall, anchor=tk.NW)
			elif tile.tile_type == tile.IS_UNKNOWN:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.unknown, anchor=tk.NW)
			else:
				print("Unknown tile type " + tile.get_tile_type())


			if tile.has_player:
				for i in ScreenInstance.player_image:
					self.create_image(col_on_graphics,row_on_graphics, image=i, anchor=tk.NW)
			if tile.has_stench:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.stench, anchor=tk.NW)
			if tile.has_breeze:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.breeze, anchor=tk.NW)
			if tile.has_glitter:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.glitter, anchor=tk.NW)
			if tile.has_wumpus:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.wumpus, anchor=tk.NW)
			if tile.has_pit:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.pit, anchor=tk.NW)
			if tile.heard_scream:
				self.create_image(col_on_graphics,row_on_graphics, image=ScreenInstance.wumpus_scream, anchor=tk.NW)

	@staticmethod
	def find_random_image(foldername:Path, bottomStartingImage = None):
		folder = foldername
		files = list(folder.iterdir())
		num = random.randint(0,len(files)-1) #both inclusive
		f = files[num]
		while f.is_dir(): #2 folders in that array
			f = files[random.randint(0,len(files)-1)]

		# print(f.absolute())
		image = tk.PhotoImage(file=f.absolute())
		if bottomStartingImage:
			if(type(bottomStartingImage) != list):
				return [bottomStartingImage,image]
			else:
				bottomStartingImage.append(image)
				return bottomStartingImage
		return image


	@staticmethod
	def load_player_image(col:int, row:int):
		playerImage = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","player","base"))
		playerImage = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","player","cloak"),bottomStartingImage=playerImage)
		playerImage = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","player","boots"),bottomStartingImage=playerImage)
		playerImage = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","player","gloves"),bottomStartingImage=playerImage)
		playerImage = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","player","draconic_head"),bottomStartingImage=playerImage)
		# playerImage = ScreenInstance.findRandomImage(Path("images","Dungeon Crawl Stone Soup Full","player","draconic_wing"),bottomStartingImage=playerImage)
		return playerImage
		


	@staticmethod
	def setup_pictures():
		ScreenInstance.pit = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","traps"))
		ScreenInstance.wumpus = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","monster"))
		ScreenInstance.glitter = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","item","gold"))
		ScreenInstance.breeze = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","floor","breeze"))
		ScreenInstance.stench = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","floor","stench"))
		ScreenInstance.wumpus_scream = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","floor","wumpusScream"))
		ScreenInstance.wall = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","wall"))
		ScreenInstance.ground = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","floor"))
		ScreenInstance.unknown = ScreenInstance.find_random_image(Path("images","Dungeon Crawl Stone Soup Full","dungeon","floor","unknown"))
		ScreenInstance.player_image = ScreenInstance.load_player_image(4,4)

		if(Variables.tile_size == 128):
			ScreenInstance.pit = ScreenInstance.pit.zoom(4,4)
			ScreenInstance.wumpus = ScreenInstance.wumpus.zoom(4,4)
			ScreenInstance.glitter = ScreenInstance.glitter.zoom(4,4)
			ScreenInstance.breeze = ScreenInstance.breeze.zoom(4,4)
			ScreenInstance.stench = ScreenInstance.stench.zoom(4,4)
			ScreenInstance.wumpus_scream = ScreenInstance.wumpus_scream.zoom(4,4)
			ScreenInstance.wall = ScreenInstance.wall.zoom(4,4)
			ScreenInstance.ground = ScreenInstance.ground.zoom(4,4)
			ScreenInstance.unknown = ScreenInstance.unknown.zoom(4,4)
			for i in range(len(ScreenInstance.player_image)):
				ScreenInstance.player_image[i] = ScreenInstance.player_image[i].zoom(4,4)


