import pygame
from settings import *
from support import *
from sprites import Generic
from random import randint, choice
from timer import Timer

class Drop(Generic):
	def __init__(self, position, surface, moving, groups, z):
		super().__init__(position, surface, groups, z)

		# Gen setup
		self.lifetime = randint(400,500)
		self.start_time = pygame.time.get_ticks()
		self.timer = Timer(self.lifetime)
		self.timer.activate()

		self.moving = moving
		if self.moving:
			self.position = pygame.math.Vector2(self.rect.topleft)
			self.direction = pygame.math.Vector2(-1,4)
			self.speed = randint(200,250)

	def update(self, dt):
		self.timer.update()
		if not self.timer.active:
			self.kill()
		if self.moving:
			self.position += self.direction * self.speed * dt
			self.rect.topleft = (round(self.position.x), round(self.position.y))

class Rain:
	def __init__(self, all_sprites):
		self.all_sprites = all_sprites
		self.rain_drops = import_folder('../graphics/rain/drops/')
		self.rain_floor = import_folder('../graphics/rain/floor/')
		self.floor_width, self.floor_height = pygame.image.load('../graphics/world/ground.png').get_size()

	def create_floor(self):
		Drop(position = (randint(0,self.floor_width),randint(0,self.floor_height)), surface = choice(self.rain_floor), moving = False, groups = self.all_sprites, z = LAYERS['rain floor'])

	def create_drops(self):
		Drop(position = (randint(0,self.floor_width),randint(0,self.floor_height)), surface = choice(self.rain_drops), moving = True, groups = self.all_sprites, z = LAYERS['rain drops'])

	def update(self):
		self.create_floor()
		self.create_drops()