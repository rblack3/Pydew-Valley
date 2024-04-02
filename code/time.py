import pygame
from random import randint

MONTHS = {1: 'Jan',
			2: 'Feb',
			3: 'Mar',
			4: 'Apr',
			5: 'May',
			6: 'Jun',
			7: 'Jul',
			8: 'Aug',
			9: 'Sep',
			10: 'Oct',
			11: 'Nov',
			12: 'Dec'}

class Time:
	def __init__(self, weather):
		self.time = pygame.time.get_ticks()
		print(self.time)
		self.day = 1
		self.month = 1
		self.luck = randint(0,10)
		#self.phase = data['phase']
		self.weather = 'rain' if weather else 'sun'
		self.year = 1

	def new_day(self):
		self.luck = randint(0,10)
		if self.day < 28 or (self.day < 30 and not self.month == 2):
			self.day += 1
		elif self.day == 28 and self.month == 2:
			self.day = 1
			self.month += 1
		elif (self.day == 30 and self.month in [9,4,6,11]) or (self.day == 31 and self.month in [1,3,5,7,8,10]):
			self.day = 1
			self.month += 1
		elif self.day == 31 and self.month == 12:
			self.day = 1
			self.month = 1
			self.year += 1

	def update(self, dt):
		if pygame.time.get_ticks() + 60 > self.time:
			print("new second")

