import pygame
from settings import *

class GUI:
	def __init(self,player):


		# GENERAL SETUP
		self.display_surface = pygame.display.get_surface()
		self.player = player



	def display(self):
		tool_surface = self.tool_surfaces[self.player.selected_tool]
		tool_rect = tool_surface.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
		self.display_surface.blit(tool_surface, tool_rect)
 
		# seeds

		seed_surface = self.seed_surfaces[self.player.selected_seed]
		seed_rect = seed_surface.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
		self.display_surface.blit(seed_surface, seed_rect)

class Overlay:
	def __init__(self, player, time):
		pygame.font.init()
		self.font = pygame.font.SysFont('Retro', 22)

		# gen setup
		self.display_surface = pygame.display.get_surface()
		self.player = player

		# Date / Time n stuff
		self.time = time
		self.date_str = time.date_string
		self.time_str = time.time_string
		self.luck = time.luck
		self.gold = self.player.gold

		#self.arrow = arrow


		# imports
		overlay_path = '../graphics/overlay/'
		self.clock_surface = pygame.transform.scale(pygame.image.load(f'{overlay_path}clock.png').convert_alpha(), (216 // 1.5, 177 // 1.5))
		self.tool_surfaces = {tool: pygame.transform.scale(pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha(), (52,60)) if tool == 'pickaxe' or tool == 'scythe' else pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
		self.seed_surfaces = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}
		self.weather_surfaces = {weather: pygame.transform.scale(pygame.image.load(f'{overlay_path}{weather}.png').convert_alpha(), (36//1.5, 24//1.5)) for weather in ['sun', 'rain']}

		self.weather_offset = (SCREEN_WIDTH - 150 + (87) // 1.5, 8 + (48//1.5))

	def display(self, dt):
		self.time.update(dt)

		self.date_str = self.time.date_string
		self.time_str = self.time.time_string
		self.luck = self.time.luck
		self.gold = self.player.gold
		self.gold_arr = ["0","0","0","0","0","0","0","0"]
		self.gold_str = str(self.gold)
		for i in range(len(self.gold_str)):
			#print(i)
			self.gold_arr[len(self.gold_arr)-1-i] = self.gold_str[len(self.gold_str)-1-i] # 1024% 10 -> [0,...,4], # 1020 % 100 = 20 
		gold_string = ' '.join(self.gold_arr)

		# GUI
		clock_surface = self.clock_surface.copy()
		clock_rect = clock_surface.get_rect(topleft = (SCREEN_WIDTH - 150, 8))
		self.display_surface.blit(clock_surface, clock_rect)
		weather_surface = self.weather_surfaces['rain']
		weather_rect = weather_surface.get_rect(topleft = self.weather_offset)
		self.display_surface.blit(weather_surface, weather_rect)

		# Date and Time
		self.font = pygame.font.SysFont('Retro', 22)
		date = self.font.render(self.date_str, False, (0, 0, 0))
		self.display_surface.blit(date, (SCREEN_WIDTH - 85,20))

		time = self.font.render(self.time_str, False, (0, 0, 0))
		self.display_surface.blit(time, (SCREEN_WIDTH - 85, 65))

		# Gold
		self.font = pygame.font.SysFont('Retro', 22)
		gold = self.font.render(gold_string, False, (150, 0, 14))
		self.display_surface.blit(gold, (SCREEN_WIDTH - 115, 106))

		# tools

		tool_surface = self.tool_surfaces[self.player.selected_tool]
		tool_rect = tool_surface.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
		self.display_surface.blit(tool_surface, tool_rect)
 
		# seeds

		seed_surface = self.seed_surfaces[self.player.selected_seed]
		seed_rect = seed_surface.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
		self.display_surface.blit(seed_surface, seed_rect)