import pygame
from settings import *
from support import *
from timer import Timer
from random import randint

class Background(pygame.sprite.Sprite):
	def __init__(self, position, surface, groups):
		super().__init__(groups)
		self.image = pygame.transform.scale(surface, (32, 32))
		self.rect = self.image.get_rect(topleft = position)
		self.z = LAYERS['inventory 1']

class Item(pygame.sprite.Sprite):
	def __init__(self, position, surface, groups, amount, item, full):
		super().__init__(groups)

		pygame.font.init()
		self.font = pygame.font.SysFont('Junimo', 25)

		self.image = pygame.transform.scale(surface, (64, 64))
		self.surface = self.image.copy()
		self.rect = self.image.get_rect(topleft = position)
		self.z = LAYERS['inventory 3']	

		self.full = full
		self.max_amount = 2
		self.amount = amount
		self.item = item if item is not None else None

		#self.update()

	def update(self, dt = pygame.time.get_ticks()):
		self.font = pygame.font.SysFont('Junimo', 25)
		self.image = self.surface.copy()
		text = self.font.render(str(self.amount), False, ('white'))
		self.image.blit(text, (40,44))
		#self.image.blit(self.surface.copy(), (0,0))

	def fix_count(self, amount):
		self.amount = amount
		self.update()

class Slots(pygame.sprite.Sprite):
	def __init__(self, position, surface, all_sprites, groups, sprite_groups, kind, bg = False):
		if not bg:
			groups.append(all_sprites)
		super().__init__(groups)

		self.all_sprites = all_sprites
		self.image = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
		self.rect = self.image.get_rect(topleft = position)
		self.z = LAYERS['inventory 2']
		self.sprite_groups = sprite_groups
		path = '../graphics/test_inventory'
		self.item_sprites = import_folder_dict(path)

		
		# ITEM STORAGE
		self.full = False
		self.item = None
		self.amount = 0
		self.max_amount = 2

		# Item
		self.kind = kind
		self.item_v_group = None
		self.item_group = None
		self.item_vis = False if kind == 'main' else True

		cursor_path = '../graphics/inventory/UI/slot_selected/animated/single_frames/'
		self.cursor_sprites = import_folder(cursor_path)
		self.isCursor = False
		self.cursor_v = None
		#if randint(0,5) == 3:
		#	self.isCursor = True
		self.cursor_num = 0
		self.cursor = Cursor(self.rect.topleft, self.cursor_sprites[self.cursor_num], [self.sprite_groups['bottom']['cursor']])
		if self.isCursor and self.item_vis:
			self.cursor_v = Cursor(self.rect.topleft, self.cursor_sprites[self.cursor_num], [self.all_sprites, self.sprite_groups['bottom']['cursor_v']])



	def update_vis(self, visibility):
		self.item_vis = visibility
		self.update_stuff()

	def add_item(self, amount, item):
		self.item = item
		if amount is not 0 and item is not None:
			self.amount = amount
			self.item = item
			if self.amount == self.max_amount:
				self.full = True
		self.update_stuff()
		if self.item_group is not None:
			self.item_group.amount = self.amount
			self.item_group.item = self.item 
			self.item_group.full = self.full
		if self.item_v_group is not None:
			self.item_v_group.full = self.full
			self.item_v_group.item = self.item
			self.item_v_group.amount = self.amount
			self.item_v_group.max_amount = self.max_amount

	def gen_v_item(self):
		self.item_v_group = Item(self.rect.topleft, self.item_sprites[self.item], [self.all_sprites, self.sprite_groups[self.kind]['item_v_sprites']], self.amount, self.item, self.full)

	def gen_item(self):
		self.item_group = Item(self.rect.topleft, self.item_sprites[self.item], [self.sprite_groups[self.kind]['item_sprites']], self.amount, self.item, self.full)

	def update_stuff(self):
		if self.item_group is None and self.item is not None:
			self.gen_item()
		if self.item_group is not None and self.item_v_group is None and self.item_vis:
			self.gen_v_item()		
		if self.isCursor and self.item_vis and self.kind == 'bottom':
			self.cursor_v = Cursor(self.rect.topleft, self.cursor_sprites[self.cursor_num], [self.all_sprites, self.sprite_groups['bottom']['cursor_v']])
		elif not self.isCursor and self.cursor_v is not None:
			self.cursor_v.kill()
			self.cursor_v = None


class Cursor(pygame.sprite.Sprite):
	def __init__(self, position, surface, groups):
		super().__init__(groups)

		self.image = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
		self.rect = self.image.get_rect(topleft = position)
		self.z = LAYERS['inventory 4']

	def update(self, position, is_pressing = False):
		pass

class Inventory:
	def __init__(self, all_sprites):

		self.all_sprites = all_sprites
		self.item_inventory = {
			'wood': 	0,
			'apple': 	0,
			'corn': 	0,
			'tomato': 	0
		}

		# SPRITE GROUPS
		# BOTTOM
		self.sprite_groups = {'bottom': 
								{'inv_sprites': pygame.sprite.Group(),
									'inv_bg_sprites': pygame.sprite.Group(),
									'item_sprites': pygame.sprite.Group(),
									'item_v_sprites': pygame.sprite.Group(),
									'inv_v_sprites': pygame.sprite.Group(),
									'cursor': pygame.sprite.Group(),
									'cursor_v': pygame.sprite.Group()},
								'main': {
										'inv_sprites': pygame.sprite.Group(),
										'inv_bg_sprites': pygame.sprite.Group(),
										'inv_v_sprites': pygame.sprite.Group(),
										'item_sprites': pygame.sprite.Group(),
										'item_v_sprites': pygame.sprite.Group(),
										'cursor': pygame.sprite.Group(),
										'cursor_v': pygame.sprite.Group()}}


		self.bottom = (SCREEN_WIDTH // 2 - 56, SCREEN_HEIGHT - 48)		
		self.b_added = False
		self.m_added = False

		self.create_grid()
		slot_path = '../graphics/inventory/UI/slots/variation_1.png'
		self.slot_image = pygame.image.load(slot_path).convert_alpha()
		bg_path = '../graphics/inventory/bg/'
		self.bg_image = import_folder_dict(bg_path)
		self.active = False
		self.timer = Timer(1000)
		self.main = False
		self.update_visibilities('bottom')

	def create_grid(self):
		self.grid = [[['main','tl', 'bg'] if (num_row == 3 and num_col == 7)
						else ['main','tlb','bg'] if (num_row == 11 and num_col == 7) 
						else ['main','trb','bg'] if (num_row == 11 and num_col == 32) 
						else ['main','blb','bg'] if (num_row == 17 and num_col == 7) 
						else ['main','brb','bg'] if (num_row == 17 and num_col == 32) 
						else ['main', 'tmb', 'bg'] if (num_row == 11 and num_col > 7 and num_col < 32)
						else ['main', 'lmb', 'bg'] if (num_row > 11 and num_row < 17 and num_col == 7)
						else ['main', 'rmb', 'bg'] if (num_row > 11 and num_row < 17 and num_col == 32)
						else ['main','tm','bg'] if (num_row == 3 and num_col > 6 and num_col < 32) 
						else ['main','tr','bg'] if (num_row == 3 and num_col == 32)
						else ['main','lm','bg'] if (num_row > 3 and num_row < 10 and num_col == 7)
						else ['main','rm','bg'] if (num_row > 3 and num_row < 10 and num_col == 32) 
						else ['main','bl','bg'] if (num_row == 10 and num_col == 7) 
						else ['main','br','bg'] if (num_row == 10 and num_col == 32)
						else ['main','bm','bg'] if ((num_row == 10 or num_row == 17) and num_col > 7 and num_col < 32)
						else ['main', 'reg'] if (num_row > 3 and num_row < 10 and num_col > 7 and num_col < 32)						
						else ['main', 'regb', 'bg'] if (num_row > 10 and num_row < 17 and num_col > 7 and num_col < 32)
						else ['bottom','tl', 'bg'] if (num_row == 19 and num_col == 7)
						else ['bottom','tm','bg'] if (num_row == 19 and num_col > 6 and num_col < 32) 
						else ['bottom','tr','bg'] if (num_row == 19 and num_col == 32)
						else ['bottom','lm','bg'] if (num_row > 19 and num_row < 22 and num_col == 7)
						else ['bottom','rm','bg'] if (num_row >19 and num_row < 22 and num_col == 32) 
						else ['bottom','bl','bg'] if (num_row == 22 and num_col == 7) 
						else ['bottom','br','bg'] if (num_row == 22 and num_col == 32)
						else ['bottom','bm','bg'] if (num_row == 22 and num_col > 7 and num_col < 32)
						else ['bottom', 'reg',] if (num_row > 19 and num_row < 21 and num_col > 7 and num_col < 32)
						else [] for num_col in range(SCREEN_WIDTH // (TILE_SIZE// 2))] for num_row in range(SCREEN_HEIGHT // (TILE_SIZE// 2))]
						# 40 cols, 23 rows

	def update_visibilities(self, type):
		for slot in self.sprite_groups[type]['inv_sprites'].sprites():
			slot.update_vis(True)
		for slot in self.sprite_groups['main' if type == 'bottom' else 'bottom']['inv_sprites'].sprites():
			slot.update_vis(False)

	def create_slots(self, visible = False, type = 'bottom'):
		if type == 'main':
			self.delete_slots(type = 'bottom' if type == 'main' else 'main', create = False)

		for num_row, row in enumerate(self.grid):
			for num_col, cell in enumerate(row):
				x = num_col * TILE_SIZE // 2
				y = num_row * TILE_SIZE // 2
				if type in cell:
					if not 'created' in cell and 'bg' not in cell and num_row % 2 == 0 and num_col % 2 == 0:
						Slots((x,y), self.slot_image, self.all_sprites, [self.sprite_groups[type]['inv_sprites']], self.sprite_groups, type, True)
						cell.append('created')
					if visible:
						if num_row % 2 == 0 and num_col % 2 == 0 and 'bg' not in cell:
							Slots((x,y), self.slot_image, self.all_sprites, [self.sprite_groups[type]['inv_v_sprites']], self.sprite_groups, type, False)
						Background((x, y), self.bg_image[cell[1]], [self.all_sprites, self.sprite_groups[type]['inv_bg_sprites']])

	def delete_slots(self, type, create = True):
		for slot in self.sprite_groups[type]['inv_v_sprites'].sprites():
			slot.kill()
		for slot in self.sprite_groups[type]['inv_bg_sprites'].sprites():
			slot.kill()
		for slot in self.sprite_groups[type]['inv_sprites'].sprites():
			if slot.item_v_group is not None:
				slot.item_v_group.kill()
				slot.item_v_group = None
		for cursor in self.sprite_groups[type]['cursor_v'].sprites():
			cursor.kill()
		if create:
			self.create_slots(True, 'main' if type == 'bottom' else 'bottom')
			self.update_visibilities('main' if type == 'bottom' else 'bottom')

	def add_item(self, item, num):
		remaining_items = num

		slot_type = ['bottom', 'main']
		for i in range(len(slot_type)):
			for sprite in self.sprite_groups[slot_type[i]]['inv_sprites'].sprites():
				if sprite.item_group is not None and sprite.item_group.full is False and sprite.item_group.item == item:
					if remaining_items + sprite.item_group.amount <= sprite.item_group.max_amount:
						sprite.add_item(sprite.item_group.amount + remaining_items, item)
						if sprite.item_v_group is not None:
							sprite.item_v_group.fix_count(sprite.amount)
						sprite.item_group.fix_count(sprite.amount)
						return
					elif remaining_items + sprite.amount > sprite.max_amount:
						remaining_items -= sprite.max_amount - sprite.amount
						sprite.add_item(sprite.max_amount, item)
						if sprite.item_v_group is not None:
							sprite.item_v_group.fix_count(sprite.amount)
						sprite.item_group.fix_count(sprite.amount)
						continue
			for inv in self.sprite_groups[slot_type[i]]['inv_sprites'].sprites():
				if inv.item == None and not inv.full:
					if remaining_items <= inv.max_amount:
						inv.add_item(remaining_items, item)
						if inv.item_v_group is not None:
							inv.item_v_group.fix_count(inv.amount)
						inv.item_group.fix_count(inv.amount)
						return
					elif remaining_items > inv.max_amount:
						remaining_items -= inv.max_amount
						inv.add_item(inv.max_amount, item)
						if inv.item_v_group is not None:
							inv.item_v_group.fix_count(inv.amount)
						inv.item_group.fix_count(inv.amount)

	def update(self):
		nums = [False, False]
		for i, thing in enumerate(['main', 'bottom']):
			for sprite in self.sprite_groups[thing]['inv_v_sprites']:
				nums[i] = True
				break
			if nums[i]:
				self.create_slots(visible = True if thing == 'bottom' else False, type = thing)

		if not self.active and not self.timer.active:
			self.active = True
			self.timer.activate()
			self.create_slots(visible = True, type = 'main')
			self.update_visibilities('main')
		elif self.timer.active:
			self.timer.update()
		elif not self.timer.active:
			self.delete_slots(type = 'main')
			self.active = False
			self.timer.activate()