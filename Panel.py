# -*- coding: utf-8 -*-

import pygame

class StatusPanel(object):
  def __init__(self, world):
    self.screen_font = pygame.font.SysFont("umpush", 16)
    self.world = world
    self.height = 166
    self.menu_width = 150
    self.menu_start = self.world.SCREEN_SIZE[0]-self.menu_width
    self.displayed_entities = []
    self.status_display_mode = "list"
    self.displayed_type = "animal"
    self.displayed_entity_number = 0

  def blitrendertext(self, text, row, screen):
    statustext = self.screen_font.render(text, True, (0,0,0))
    screen.blit(statustext, (10, 20*row, 15, 15))

  def define_displayed_entities(self):
    self.displayed_entities = []
    for entity in self.world.entities.itervalues():
      entity.indicated = False
      if entity.typestring == self.displayed_type:
	self.displayed_entities.append(entity)

  def draw_menu(self, screen):
    menu_start = self.menu_start
    pygame.draw.rect(screen, (180, 200, 210), pygame.Rect((menu_start,0),(self.world.SCREEN_SIZE[0],self.height)))
    screen.blit(self.screen_font.render("Quit", True, (0,0,0)), (menu_start, 0, 15, 15))
    screen.blit(self.screen_font.render("Animals", True, (0,0,0)), (menu_start, 20, 15, 15))
    screen.blit(self.screen_font.render("Sites", True, (0,0,0)), (menu_start, 40, 15, 15))
    screen.blit(self.screen_font.render("Humans", True, (0,0,0)), (menu_start, 60, 15, 15))
    screen.blit(self.screen_font.render("List/Single", True, (0,0,0)), (menu_start, 80, 15, 15))
    screen.blit(self.screen_font.render("<", True, (0,0,0)), (menu_start, 100, 15, 15))
    screen.blit(self.screen_font.render(">", True, (0,0,0)), (menu_start + 20, 100, 15, 15))

  def draw_panel(self, screen):
    rectangle = pygame.Rect((0,0),(self.world.SCREEN_SIZE[0],self.height))
    pygame.draw.rect(screen, (180, 210, 210), rectangle)
    self.define_displayed_entities()
    if self.status_display_mode == "list":
      for entity in self.displayed_entities:
	entity.indicated = True
	status_text = entity.__str__()
	self.blitrendertext(status_text, self.displayed_entities.index(entity), screen)

    elif self.status_display_mode == "single":
      for entity in self.displayed_entities:
	if self.displayed_entities.index(entity) == self.displayed_entity_number:
	  entity.indicated = True
	  description_list = entity.description_list()
	  for entry in description_list:
	    self.blitrendertext(entry, description_list.index(entry), screen)
      
    self.draw_menu(screen)

    #time_of_day_symb = screen_font.render(time_of_day, True, (0,0,0))
    #screen.blit(time_of_day_symb, (700, 20, 15, 15))
    #time_pic = screen_font.render(str(round(time_o_clock,2)), True, (0,0,0))
    #screen.blit(time_pic, (750, 20, 15, 15))
    #zeitraffer_pic = screen_font.render("Zeitraffer(Click): " + str(zeitraffer), True, (0,0,0))
    #screen.blit(zeitraffer_pic, (700, 40, 15, 15))