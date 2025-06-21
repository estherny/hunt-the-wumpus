from GameInstance import GameInstance
from Variables import Variables
from DrBsGui import DrBsGui
# Variables.GAME_PLAY_TYPE = Variables.GamePlayType.KEYBOARD
# if Variables.GAME_PLAY_TYPE == Variables.GamePlayType.KEYBOARD:
d = DrBsGui()
d.m.mainloop()
# else:
# 	maps = GameInstance.generate_maps_with_1_wall_and_2_pits(6,6); #outside padded with walls
# 	Variables.AUTO_ADVANCE_ROUNDS = False
# 	for i in range(0,100):
# 		g =  GameInstance(map=maps.pop(), screen_instance=None)
# 		twice = 0
# 		while twice < 2:
# 			g.advance_time()
# 			if g.game_is_over():
# 				twice+=1

