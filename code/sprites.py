import pygame
from settings import *
from random import randint, choice
from timer import Timer

class Generic(pygame.sprite.Sprite):
	def __init__(self, pos, surface, groups, z = LAYERS['main']):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft = pos)
		self.z = z
		self.hitbox = self.rect.copy().inflate(-self.rect.width *0.2, -self.rect.height * 0.75)

class Interaction(Generic):
	def __init__(self, position, size, groups, name):
		surface = pygame.Surface(size)
		super().__init__(position, surface, groups)
		self.name = name

class Water(Generic):
	def __init__(self, pos, frames, groups, z = LAYERS['water']):
		self.frames = frames
		self.frame_index = 0

		super().__init__(pos = pos, surface = self.frames[self.frame_index], groups = groups, z = z)

	def animate(self, dt):
		self.frame_index += 4 * dt
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self, dt):
		self.animate(dt)

class Flower(Generic):
	def __init__(self, pos, surface, groups):
		super().__init__(pos, surface, groups)
		self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Particle(Generic):
	def __init__(self, pos, surface, groups, z, duration = 200):
		super().__init__(pos, surface, groups, z)

		self.start_time = pygame.time.get_ticks()
		self.duration = duration

		mask_surface = pygame.mask.from_surface(self.image)
		new_surface = mask_surface.to_surface()
		new_surface.set_colorkey((0,0,0))
		self.image = new_surface

	def damage(self):
		pass

	def update(self, dt):
		current_time = pygame.time.get_ticks()
		if current_time - self.start_time > self.duration:
			self.kill()

class Mineral(Generic):
	def __init__(self, pos, surface, all_sprites, groups, name, player_add, hp):
		self.groups = groups[:]
		self.groups.append(all_sprites)
		super().__init__(pos, surface, self.groups)

		self.health = hp
		self.alive = True
		self.all_sprites = all_sprites

		self.player_add = player_add
		self.name = name

	def damage(self):
		self.health -= 1

	def check_death(self):
		if self.health <= 0:
			Particle(self.rect.topleft, self.image, self.all_sprites, LAYERS['fruit'], 500)
			if self.name == "Grass":
				if randint(0,10) < 2:
					self.player_add(self.name)
			elif self.name == "Rock":
				self.player_add(self.name, randint(3,5))
			elif self.name == "wood":
				print("adding wood")
				self.player_add('wood', randint(3,5))
			self.kill()
			
	def update(self, dt):
		if self.alive:
			self.check_death()

class Tree(Generic):
	def __init__(self, pos, surface, all_sprites, groups, name, player_add):
		self.groups = groups[:]
		self.groups.append(all_sprites)
		super().__init__(pos, surface, self.groups)

		self.health = 5
		self.alive = True
		stump_path = f'../graphics/stumps/{"small" if name == "Small" else "large"}.png'
		self.stump_surface = pygame.image.load(stump_path).convert_alpha()
		self.invul_timer = Timer(200)
		self.isStump = False
		self.stump_hp = 5
		self.all_sprites = all_sprites

		##self.apple_surface = pygame.image.load('../graphics/fruit/apple.png')
		#self.apple_positions = APPLE_POS[name]
		#self.apple_sprites = pygame.sprite.Group()
		#self.create_fruit()

		self.player_add = player_add

	def damage(self):
		if not self.isStump:
			self.health -= 1

			#if len(self.apple_sprites.sprites()) > 0:
			#	random_apple = choice(self.apple_sprites.sprites())
			#	Particle(random_apple.rect.topleft, random_apple.image, 
			#			self.all_sprites, z = LAYERS['fruit'])
			#	self.player_add('apple')
			#	random_apple.kill()
		else:
			self.stump_hp -= 1

	def check_death(self):
		if self.health <= 0 and self.alive:
			Particle(self.rect.topleft, self.image, self.all_sprites, LAYERS['fruit'], 500)
			self.image = self.stump_surface
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
			self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
			self.alive = False
			self.isStump = True #randint(5,10)
			self.player_add('wood', randint(15,20))
		elif self.isStump and self.stump_hp <= 0:
			Particle(self.rect.topleft, self.image, self.all_sprites, LAYERS['fruit'], 500)
			self.player_add('wood', randint(10,15)) #randint(15,20)
			self.kill()
			
	def update(self, dt):
		#if self.alive or self.isStump:
		self.check_death()

	#def create_fruit(self):
	#	for pos in self.apple_positions:
	#		if randint(0,10) < 2:
	#			x = pos[0] + self.rect.left
	#			y = pos[1] + self.rect.top
	#			Generic(
	#				pos = (x,y), 
	#				surface = self.apple_surface, 
	#				groups = [self.all_sprites, self.apple_sprites],
	#				z = LAYERS['fruit'])