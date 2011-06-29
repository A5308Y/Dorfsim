# -*- coding: utf-8 -*-

import pygame, sys
from pygame.locals import *

class InputChecker():
  def __init__(self):
    self.last_pressed_cooldown = 0

  def check_input(self, world, panel, time_passed):
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_UP]:
      world.camera_y += 10
    if pressed_keys[K_DOWN]:
      world.camera_y -= 10
    if pressed_keys[K_LEFT]:
      world.camera_x += 10
    if pressed_keys[K_RIGHT]:
      world.camera_x -= 10
    if self.last_pressed_cooldown > 0:
      self.last_pressed_cooldown -= time_passed
    if pygame.mouse.get_pressed()[0] and self.last_pressed_cooldown <= 0:
      self.last_pressed_cooldown = 100
      mouse_x = pygame.mouse.get_pos()[0]
      mouse_y = pygame.mouse.get_pos()[1]
      if mouse_x >= panel.menu_start:
	if mouse_y <= 20:
	  exit_game()
	elif mouse_y <= 40:
	  panel.displayed_type = "animal"
	  panel.displayed_entity_number = 0
	elif mouse_y <= 60:
	  panel.displayed_type = "site"
	  panel.displayed_entity_number = 0
	elif mouse_y <= 80:
	  panel.displayed_type = "human"
	  panel.displayed_entity_number = 0
	elif mouse_y <= 100:
	  if panel.status_display_mode == "list":
	    panel.status_display_mode = "single"
	  else:
	    panel.status_display_mode = "list"
	elif mouse_y <= 120:
	  if mouse_x <= panel.menu_start + 15:
	    panel.displayed_entity_number -= 1 
	    panel.displayed_entity_number = panel.displayed_entity_number % len(panel.displayed_entities)
	  else:
	    panel.displayed_entity_number += 1 % len(panel.displayed_entities)
	    panel.displayed_entity_number = panel.displayed_entity_number % len(panel.displayed_entities)
	    
def exit_game():
    sys.exit()