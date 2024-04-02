import pygame
from settings import *
from support import *
from timer import Timer
from random import randint, choice

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, group, sprites, soil_layer, inventory):
		super().__init__(group)

		self.import_assets()
		self.status = 'down_idle'
		self.frame_index = 0

		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(center = pos)
		self.z = LAYERS['main']

		# movement
		self.direction = pygame.math.Vector2((0,0))
		self.pos = pygame.math.Vector2((pos))
		self.speed = 250

		# collision
		self.hitbox = self.rect.copy().inflate((-126, -70))
		self.collision_sprites = sprites['collision_sprites']

		# Timers
		self.timers = {
			'tool use': Timer(350, self.use_tool),
			'tool switch': Timer(200),
			'seed use': Timer(350, self.use_seed),
			'seed switch': Timer(200),
			'mouse click': Timer(500),
			'cursor switch': Timer(300)
		}

		# tools
		self.tools = ['hoe', 'axe', 'water', 'scythe', 'pickaxe']
		self.tool_index = 1
		self.selected_tool = self.tools[self.tool_index]

		# seeds 
		self.seeds = ['corn', 'tomato']
		self.seed_index = 0
		self.selected_seed = self.seeds[self.seed_index]

		# inventory
		self.item_inventory = {
			'wood': 	0,
			'apple': 	0,
			'corn': 	0,
			'tomato': 	0
		}
		self.inventory = inventory
		self.inventory.create_slots(visible = True, type = 'bottom')
		self.gold = 10140329

		# Interactions
		self.tree_sprites = sprites['tree_sprites']
		self.rock_sprites = sprites['rock_sprites']
		self.grass_sprites = sprites['grass_sprites']
		self.log_sprites = sprites['log_sprites']
		self.interaction = sprites['interaction_sprites']
		self.sleep = False
		self.soil_layer = soil_layer


		# Cursor
		self.cursorPos = 0
		if self.inventory.sprite_groups['bottom']['inv_sprites'].sprites() is not None:
			sprite = self.inventory.sprite_groups['bottom']['inv_sprites'].sprites()[0]
			sprite.isCursor = True
			sprite.update_stuff()

	def use_tool(self):
		self.get_target_pos()
		if self.selected_tool == 'hoe':
			self.soil_layer.get_hit(self.target_pos)

		if self.selected_tool == 'axe':
			for log in self.log_sprites.sprites():
				if log.rect.collidepoint(self.target_pos):
					log.damage()
			for tree in self.tree_sprites.sprites():
				if tree.rect.collidepoint(self.target_pos):
					tree.damage()
			
		if self.selected_tool == 'scythe':
			for grass in self.grass_sprites.sprites():
				if grass.rect.collidepoint(self.target_pos):
					grass.damage()
		if self.selected_tool == 'pickaxe':
			for rock in self.rock_sprites.sprites():
				if rock.rect.collidepoint(self.target_pos):
					rock.damage()

		if self.selected_tool == 'water':
			self.soil_layer.water(self.target_pos)

	def get_target_pos(self):
		if pygame.mouse.get_pressed()[0] or self.timers['mouse click'].active:
			self.target_pos = pygame.mouse.get_pos()
		else:
			self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

	def use_seed(self):
		self.soil_layer.plant_seed(self.target_pos, self.selected_seed)

	def import_assets(self):
		self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 
							'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [], 
							'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
							'right_axe': [],'left_axe': [], 'up_axe': [],'down_axe': [],
							'right_water': [],'left_water': [], 'up_water': [], 'down_water': [],
							'right_pickaxe': [],'left_pickaxe': [], 'up_pickaxe': [], 'down_pickaxe': [],
							'right_scythe': [],'left_scythe': [], 'up_scythe': [], 'down_scythe': [],}

		for animation in self.animations.keys():
			full_path = '../graphics/character/' + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self, dt):
		self.frame_index += 4 * dt
		if self.frame_index >= len(self.animations[self.status]):
			self.frame_index = 0
		self.image = self.animations[self.status][int(self.frame_index)]

	def get_status(self):
		#idle
		if self.direction.magnitude() == 0:
			self.status = self.status.split('_')[0] + '_idle'

		# tool use
		if self.timers['tool use'].active:
			self.status = self.status.split('_')[0] + '_' + self.selected_tool

	def input(self):
		keys = pygame.key.get_pressed()


		if not self.timers['tool use'].active and not self.sleep:
			if not self.inventory.active:
				# directions
				if keys[pygame.K_UP]:
					self.direction.x = 0
					self.direction.y = -1
					self.status = 'up'
				elif keys[pygame.K_DOWN]:
					self.direction.x = 0
					self.direction.y = 1
					self.status = 'down'
				elif keys[pygame.K_LEFT]:
					self.direction.y = 0
					self.direction.x = -1
					self.status = 'left'
				elif keys[pygame.K_RIGHT]:
					self.direction.y = 0
					self.direction.x = 1
					self.status = 'right'
				else:
					self.direction.x = 0
					self.direction.y = 0

				if keys[pygame.K_c] and not self.timers['cursor switch'].active:
					self.timers['cursor switch'].activate()
					new_sprite = self.inventory.sprite_groups['bottom']['inv_v_sprites'].sprites()[self.cursorPos]
					new_sprite.isCursor = False
					new_sprite.update_stuff()
					new_sprite = self.inventory.sprite_groups['bottom']['inv_sprites'].sprites()[self.cursorPos]
					new_sprite.isCursor = False
					new_sprite.update_stuff()
					self.cursorPos = self.cursorPos + 1 if self.cursorPos + 1 < len(self.inventory.sprite_groups['bottom']['inv_v_sprites'].sprites()) else 0
					if self.inventory.sprite_groups['bottom']['inv_sprites'].sprites() is not None:
						sprite = self.inventory.sprite_groups['bottom']['inv_sprites'].sprites()[self.cursorPos]
						sprite.isCursor = True
						sprite.update_stuff()
		
				# tool use

				if pygame.mouse.get_pressed()[0] or keys[pygame.K_t]:
					if pygame.mouse.get_pressed()[0]:
						self.target_pos = pygame.mouse.get_pos()
						self.timers['mouse click'].activate()
					self.timers['tool use'].activate()
					self.direction = pygame.math.Vector2()
					self.frame_index = 1

				# change tool
				if keys[pygame.K_n] and not self.timers['tool switch'].active:
						self.timers['tool switch'].activate()
						self.tool_index += 1
						self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
						self.selected_tool = self.tools[self.tool_index]


				# seed use
				if keys[pygame.K_r]:
					self.timers['seed use'].activate()
					self.direction = pygame.math.Vector2()
					self.frame_index = 1

				# change seed
				if keys[pygame.K_m] and not self.timers['seed switch'].active:
						self.timers['seed switch'].activate()
						self.seed_index += 1
						self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
						self.selected_seed = self.seeds[self.seed_index]

				# interaction
				if keys[pygame.K_e]:
					collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
					if collided_interaction_sprite:
						if collided_interaction_sprite[0].name == 'Trader':
							pass
						elif collided_interaction_sprite[0].name == 'Bed':
							self.status = 'left_idle'
							self.sleep = True

			if keys[pygame.K_i]:
				self.direction = pygame.math.Vector2()
				self.inventory.update()

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def collider(self, direction):
		for sprite in self.collision_sprites.sprites():
			if hasattr(sprite, 'hitbox'):
				if sprite.hitbox.colliderect(self.hitbox):
					if direction == 'horizontal':
						if self.direction.x > 0: # move right
							self.hitbox.right = sprite.hitbox.left
						if self.direction.x < 0: # move left
							self.hitbox.left = sprite.hitbox.right
						self.rect.centerx = self.hitbox.centerx
						self.pos.x = self.hitbox.centerx
					if direction == 'vertical':
						if self.direction.y > 0: # down
							self.hitbox.bottom = sprite.hitbox.top
						if self.direction.y < 0: # up
							self.hitbox.top = sprite.hitbox.bottom
						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

	def move(self, dt):
		#normalize a vector
		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()

		# hor movement

		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collider('horizontal')

		# vert movement

		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collider('vertical')

	def update(self, dt):
		#if randint(0,10) < 5:
		#	self.gold += randint(0,100)
		self.gold = randint(0,1000000)
		self.input()
		self.get_status()
		self.update_timers()
		self.get_target_pos()
		self.animate(dt)
		self.move(dt)
		#print(self.item_inventory)

