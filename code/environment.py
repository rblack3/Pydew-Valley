import pygame
from random import randint

MONTHS = {1: 'Spring',
			2: 'Summer',
			3: 'Fall',
			4: 'Winter'}

class Time:
	def __init__(self, weather):
		self.time = 0
		print(self.time)
		self.day = 1
		self.month = 1
		self.luck = randint(0,10)
		#self.phase = data['phase']
		self.weather = 'rain' if weather else 'sun'
		self.year = 1
		self.minute = 0
		self.converted_min = str(self.minute) if self.minute > 9 and self.minute < 60 else '0' + str(self.minute)
		self.hour = 7
		self.morn = True
		self.pm =  'AM' if self.morn else 'PM'
		self.time_string = str(self.hour) + ":" + str(self.converted_min) + self.pm
		self.date_string = MONTHS[self.month] + " " + str(self.day)


	def new_day(self):
		self.luck = randint(0,10)
		if self.day == 31:
			self.day = 1
			if self.month < 4:
				self.month += 1
			else:
				self.month = 1
				self.year += 1
		else:
			self.day += 1

	def update(self, dt):
		self.time += dt
		if self.time > 0:
			self.time = 0
			if self.minute >= 59:
				if self.hour == 11 and not self.morn:
					self.new_day()
				self.minute = 0
				if self.hour < 12:
					self.hour += 1
					if self.hour == 12:
						self.morn = not self.morn
				else:
					self.hour = 1
					#self.morn = not self.morn
			else: self.minute += 1
			self.pm =  'AM' if self.morn else 'PM'
			self.converted_min = str(self.minute) if self.minute > 9 and self.minute < 60 else '0' + str(self.minute)
			self.time_string = str(self.hour) + ":" + str(self.converted_min) + self.pm
			self.date_string = MONTHS[self.month] + " " + str(self.day)
			#MONTHS[self.month] + str(self.day) + "  " + str(self.hour) + ":" + str(self.converted_min) + self.pm)

