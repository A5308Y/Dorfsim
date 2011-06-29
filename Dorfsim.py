# -*- coding: utf-8 -*-

import pygame, random, dorflib, Panel, Input
from dorflib import *
from pygame.locals import *

SCREEN_SIZE = (1000, 600)

def run():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
  pygame.display.set_caption('Dorfsimulator')
  world = World(SCREEN_SIZE)
  panel = Panel.StatusPanel(world)
  input_checker = Input.InputChecker()
  clock = pygame.time.Clock()
  world.populate()

  while True:

    for event in pygame.event.get():
      if event.type == QUIT:
	return

    time_passed = clock.tick(30)
    
    input_checker.check_input(world, panel, time_passed)
    world.process(time_passed)

    screen.set_clip(0, panel.height, *SCREEN_SIZE)
    world.render(screen)
    screen.set_clip(0, 0, SCREEN_SIZE[0], panel.height)
    panel.draw_panel(screen)
    pygame.display.update()

if __name__ == "__main__":
  run()