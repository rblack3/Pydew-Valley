import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import randint

class SoilTile(pygame.sprite.Sprite):
	def __init__(self, position, surface, groups):
		super().__init__(groups)

		self.image = surface
		self.rect = self.image.get_rect(topleft = position)
		self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
	def __init__(self, position, surface, groups):
		super().__init__(groups)

		self.image = surface
		self.rect = self.image.get_rect(topleft = position)
		self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
	def __init__(self, plant_type, groups, soil, check_watered):
		super().__init__(groups)

		# Setup
		self.plant_type = plant_type
		self.frames = import_folder_dict(f'../graphics/fruit/{plant_type}/')
		self.soil = soil
		self.check_watered = check_watered


		# Growing
		self.max_age = len(self.frames) - 1
		self.age = 0
		self.grow_speed = GROW_SPEED[plant_type]
		self.harvestable = False

		# Sprite
		self.image = self.frames[str(self.age)]
		self.y_offset = -16 if plant_type == 'corn' else -8
		self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
		self.z = LAYERS['ground plant']

	def grow(self):
		if self.check_watered(self.rect.center):
			print(self.age)
			self.age += self.grow_speed
			if int(self.age) < 3:
				self.z = LAYERS['main']
				self.hitbox = self.rect.copy().inflate(-26, self.rect.height * 0.4)
			if self.age >= 3:
				#self.age = 0
				self.harvestable = True

			self.image = self.frames[str(int(self.age))]
			self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))

class SoilLayer:
	def __init__(self, all_sprites, collision_sprites):

		self.all_sprites = all_sprites
		self.collision_sprites = collision_sprites
		self.soil_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()
		self.plant_sprites = pygame.sprite.Group()

		self.soil_surfaces = import_folder_dict('../graphics/soil/')
		self.water_surfaces = import_folder_dict('../graphics/soil_water/')
		
		self.create_soil_grid()
		self.create_hit_rects()

	def create_soil_grid(self):
		ground = pygame.image.load('../graphics/world/fullset.png')
		h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

		self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
		for x, y, _ in load_pygame('../data/new_map.tmx').get_layer_by_name('Farmable').tiles():
			self.grid[y][x].append('F')

	def create_hit_rects(self):
		self.hit_rects = []
		for num_row, row in enumerate(self.grid):
			for num_col, cell in enumerate(row):
				if 'F' in cell:
					x = num_col * TILE_SIZE
					y = num_row * TILE_SIZE
					rect = pygame.Rect(x,y, TILE_SIZE, TILE_SIZE)
					self.hit_rects.append(rect)

	def get_hit(self, point):
		for rect in self.hit_rects:
			if rect.collidepoint(point):
				y = rect.y // TILE_SIZE
				x = rect.x // TILE_SIZE
				if 'F' in self.grid[y][x]:
					self.grid[y][x].append('X')
					self.create_soil_tiles()
					if self.raining:
						self.water_all()

	def water_all(self):
		for soil_sprite in self.soil_sprites.sprites():
			x = soil_sprite.rect.x // TILE_SIZE
			y = soil_sprite.rect.y // TILE_SIZE
			if 'W' not in self.grid[y][x]:
				self.grid[y][x].append('W')
				WaterTile(soil_sprite.rect.topleft, 
					self.water_surfaces[str(randint(0,2))], 
					[self.all_sprites, self.water_sprites])

	def water(self, target_position):
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_position):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				if 'W' not in self.grid[y][x]:
					self.grid[y][x].append('W')
					WaterTile(soil_sprite.rect.topleft, 
						self.water_surfaces[str(randint(0,2))], 
						[self.all_sprites, self.water_sprites])

	def check_watered(self, position):
		x = position[0] // TILE_SIZE
		y = position[1] // TILE_SIZE

		cell = self.grid[y][x]
		return 'W' in cell

	def plant_seed(self, target_position, seed):
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_position):
				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				if 'P' not in self.grid[y][x] and 'W' in self.grid[y][x]:
					self.grid[y][x].append('P')
					self.plant_surfaces = import_folder_dict(f'../graphics/fruit/{seed}/')
					Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

	def update_plants(self):
		for plant in self.plant_sprites.sprites():
			plant.grow()

	def reset_tiles(self):
		for sprite in self.water_sprites.sprites():
			sprite.kill()
			x = sprite.rect.x // TILE_SIZE
			y = sprite.rect.y // TILE_SIZE
			if 'W' in self.grid[y][x]:
				self.grid[y][x].remove('W')

	def create_soil_tiles(self):
		self.soil_sprites.empty()
		for num_row, row in enumerate(self.grid):
			for num_col, cell in enumerate(row):
				if 'X' in cell:
					x = num_col * TILE_SIZE
					y = num_row * TILE_SIZE

					t = 'X' in self.grid[num_row - 1][num_col] #if num_row > 0 else False
					r = 'X' in self.grid[num_row][num_col + 1] #if num_col < len(row) - 1 else False
					l = 'X' in self.grid[num_row][num_col - 1] #if num_col > 0 else False
					b = 'X' in self.grid[num_row + 1][num_col] #if num_row < len(self.grid) - 1 else False

					tile_type = 'o'

					if not r and not l and not b and t:
						tile_type = 'top'
					elif not r and not l and not b and not t:
						tile_type = 'o'	
					elif not r and not l and b and t:
						tile_type = 'tb'
					elif not r and not l and b and not t:
						tile_type = 't'
					elif not r and l and not b and t:
						tile_type = 'br'
					elif not r and l and not b and not t:
						tile_type = 'r'
					elif not r and l and b and t:
						tile_type = 'rm'
					elif not r and l and b and not t:
						tile_type = 'tr'
					elif r and not l and not b and t:
						tile_type = 'bl'
					elif r and not l and not b and not t:
						tile_type = 'l'	
					elif r and not l and b and t:
						tile_type = 'lm'
					elif r and not l and b and not t:
						tile_type = 'tl'
					elif r and l and not b and t:
						tile_type = 'bm'
					elif r and l and not b and not t:
						tile_type = 'lr'
					elif r and l and b and t:
						tile_type = 'x'
					elif r and l and b and not t:
						tile_type = 'tm'



					SoilTile((x,y), self.soil_surfaces[tile_type], [self.all_sprites, self.soil_sprites])

