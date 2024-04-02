import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, Flower, Tree, Interaction, Mineral, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain
from random import randint
from inventory import Inventory
from environment import Time

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()

		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.grass_sprites = pygame.sprite.Group()
		self.log_sprites = pygame.sprite.Group()
		self.rock_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()


		# Rain
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 3

		# Inventory
		self.inventory = Inventory(self.all_sprites)

		# Soil
		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.soil_layer.raining = self.raining
		self.player = 0
		self.setup()

		# Overlay
		self.time = Time(self.raining)
		self.overlay = Overlay(self.player, self.time)

		# Reset
		self.transition = Transition(self.reset, self.player)

	def setup(self):
		tmx_data = load_pygame('../data/new_map.tmx')

		# HOUSE

		for layer in ['Ground']:
			for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x*TILE_SIZE, y * TILE_SIZE), surface, self.all_sprites, LAYERS['ground'])

		#for layer in ['HouseWalls', 'HouseFurnitureTop']:
		#	for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
		#		Generic((x*TILE_SIZE, y * TILE_SIZE), surface, self.all_sprites)


		## FENCE
		#for x, y, surface in tmx_data.get_layer_by_name('Fence').tiles():
		#	Generic((x*TILE_SIZE, y * TILE_SIZE), surface, [self.all_sprites, self.collision_sprites])

		# Grass

		for obj in tmx_data.get_layer_by_name('Grass'):
			if obj.image is not None:
				Mineral((obj.x, obj.y), obj.image, self.all_sprites,
					[self.collision_sprites, self.grass_sprites], 
					obj.name, player_add = self.player_add, hp = 1)

		# Rocks

		for obj in tmx_data.get_layer_by_name('Rocks'):
			if obj.image is not None:
				Mineral((obj.x, obj.y), obj.image, self.all_sprites,
					[self.collision_sprites, self.rock_sprites], 
					obj.name, player_add = self.player_add, hp = 3)
		# Logs
		for obj in tmx_data.get_layer_by_name('Log'):
			if obj.image is not None:
				Mineral((obj.x, obj.y), pygame.transform.scale(obj.image.convert_alpha(),(64,64)), self.all_sprites,
					[self.collision_sprites, self.log_sprites], 
					obj.name, player_add = self.player_add, hp = 3)


		# WATER
		water_frames = import_folder('../graphics/water')

		for x, y, surface in tmx_data.get_layer_by_name('Water').tiles():
			Water((x*TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

		# TREES
		for obj in tmx_data.get_layer_by_name('Trees'):
			if obj.image is not None:
				Tree((obj.x, obj.y), obj.image.convert_alpha(), self.all_sprites,
					[self.collision_sprites, self.tree_sprites], 
					obj.name, player_add = self.player_add)


		# FLOWERS
		for obj in tmx_data.get_layer_by_name('Decoration'):
			Flower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		# Collision Tiles
		for x, y, surface, in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x* TILE_SIZE,y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
 		
		# Player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player((obj.x, obj.y), 
					self.all_sprites, 
					sprites = {
					'collision_sprites': self.collision_sprites,
					'tree_sprites': self.tree_sprites, 
					'interaction_sprites':  self.interaction_sprites,
					'rock_sprites': self.rock_sprites,
					'grass_sprites': self.grass_sprites,
					'log_sprites': self.log_sprites},
					soil_layer = self.soil_layer,
					inventory = self.inventory)

			if obj.name == 'Bed':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)


		Generic(pos = (0,0), surface = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
				groups = self.all_sprites, z = LAYERS['ground'])

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable:
					print(plant.rect)
					print(self.player.rect)
					if plant.rect.colliderect(self.player.rect):
						self.player_add(plant.plant_type)
						Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
						if 'P' in self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE]:
							self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
						plant.kill()

	def player_add(self, item, num = 1):

		#self.player.item_inventory[item] += num

		self.inventory.add_item(item, num)

	def reset(self):
		# Grow plants
		self.soil_layer.update_plants()

		# GUI Update
		self.time.new_day()

		# soil
		self.soil_layer.reset_tiles()
		self.raining = randint(0,10) > 3
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()
		for tree in self.tree_sprites.sprites():
			if len(tree.apple_sprites.sprites()) > 0:
				for apple in tree.apple_sprites.sprites():
					apple.kill()
			tree.create_fruit()

	def run(self, dt):
		self.display_surface.fill('black')
		#self.all_sprites.draw(self.display_surface)
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)
		self.plant_collision()
		self.overlay.display(dt)

		if self.raining:
			self.rain.update()

		if self.player.sleep:
			self.transition.play(dt)
			if self.raining:
				self.soil_layer.water_all()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y =	player.rect.centery - SCREEN_HEIGHT / 2

		for layer in LAYERS.values():
			#if layer > 10:
			#	print(layer)
			for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
				#	Wif sprite.z == LAYERS['fruit']:
				#	print("should be drawing apple")
					if layer > 10:
						self.display_surface.blit(sprite.image, sprite.rect.copy())
					elif layer == 9:
						#print("Apple rendered")
						offset_rect = sprite.rect.copy()
						offset_rect.center -= self.offset
						self.display_surface.blit(sprite.image, offset_rect)
					else:
						offset_rect = sprite.rect.copy()
						offset_rect.center -= self.offset
						self.display_surface.blit(sprite.image, offset_rect)

					#if sprite == player:
						#pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
						#hitbox_rect = player.hitbox.copy()
						#hitbox_rect.center = offset_rect.center
						#pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
						#target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
						#pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)


