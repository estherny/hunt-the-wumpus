import tkinter as tk
import random
from pathlib import Path
from ScreenInstance import ScreenInstance

class DrBsGui:
	def __init__(self, file:Path=None, parent=None):
		self.m = tk.Tk()
		self.m.title("Dr Bs Dungeon Crawler")
		# self.m.geometry("600x200")
		self.screen = ScreenInstance(4,4)

		self.m.geometry(str(self.screen.width) + "x"+str(self.screen.height))
		print(str(self.screen.width) + "x"+str(self.screen.height))
		self.setup_events()

	def setup_events(self):
		self.m.bind("<Key>", self.key_pressed)

	def key_pressed(self, keyevent):
		# print("Key pressed")
		self.screen.game_instance.set_next_move(keyevent)
