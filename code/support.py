import pygame, os

def import_folder(path):
	surface_list = []
	for filename in os.listdir(path):
		if filename.endswith(('.png', '.jpg', '.bmp')):
			full_path = os.path.join(path, filename)
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)
	return surface_list

def import_folder_dict(folder_path):
	surface_dict = {}
	for filename in os.listdir(folder_path):
		if filename.endswith(('.png', '.jpg', '.bmp')):
			full_path = os.path.join(folder_path, filename)
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[filename.split('.')[0]] = image_surf
	return surface_dict
    
"""
def import_folder_dict(path):
	surface_dict = {}

	for _, _, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[image.split('.')[0]] = image_surf

	return surface_dict"""