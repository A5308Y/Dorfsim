 # -*- coding: utf-8 -*-

import pygame, random, sys, Vector2, Panel
from Vector2 import *
import Statemachine
from Statemachine import *
import Projects
from Projects import *

class World(object):
  def __init__(self, SCREEN_SIZE):
    self.entities={}
    self.add_entity_cache=[]
    self.entity_id = 0
    self.SCREEN_SIZE = SCREEN_SIZE
    self.background = pygame.surface.Surface(SCREEN_SIZE).convert()
    self.background.fill((255,255,255))
    self.camera_x = self.camera_y = 0
    self.indicator_symb = pygame.image.load("pics/indicator.png").convert_alpha()

  def add_entity(self, entity):
    self.entities[self.entity_id] = entity
    entity_id = self.entity_id
    self.entity_id += 1

  def remove_entity(self, entity):
    del self.entities[entity_id]

  def get(self, entity_id):
    if entity_id in self.entities:
      return self.entities[entity_id]
    else:
      return None

  def process(self, time_passed):
    self.time_passed_seconds = time_passed / 1000.0
    self.time_passed = time_passed
    for entity in self.entities.itervalues():
      entity.process(self.time_passed_seconds)
    for entity in self.add_entity_cache:
      self.add_entity(entity)
    self.add_entity_cache=[]

  def render(self, surface):
    surface.blit(self.background, (0,0))
    for entity in self.entities.itervalues():
      entity.render(surface)
      if entity.indicated == True:
	self.indicate(entity, surface, self.indicator_symb)

  def indicate(self, entity, surface, indicator):
    x = entity.location.x + entity.world.camera_x
    y = entity.location.y + entity.world.camera_y
    w, h = self.indicator_symb.get_size()
    surface.blit(indicator, (x-w/2, y-h/2 - h))

  def get_close_entity(self, name, location, range=100.):
    for entity in self.entities.itervalues():
      if entity.typestring == name:
	distance = location.get_distance_to(entity.location)
	if distance < range:
	  return entity
    return None

  def closest_entity_in_list(self, animal, entity_list):
    nearest_entity = None
    min_distance = -1
    for entity in entity_list:
      distance = entity.location.get_distance_to(animal.location)
      if distance <= min_distance or min_distance == -1:
	min_distance = distance
	nearest_entity = entity
    return nearest_entity

  def entities_of_type(self, type):
    returnlist = []
    for entity in self.entities.itervalues():
      if entity.typestring == type:
	returnlist.append(entity)
    return returnlist

  def populate(self):
    w, h = self.SCREEN_SIZE
    picfolder="pics/"
    animal_image = pygame.image.load(picfolder + "bear.png").convert_alpha()
    site_image = pygame.image.load(picfolder + "ziel.png").convert_alpha()
    human_image = pygame.image.load(picfolder + "person.png").convert_alpha()

    for site in xrange(1):
      site = Farm(self)
      site.location = Vector2(random.randint(0,w), random.randint(0,h))
      self.add_entity(site)

    for site in xrange(3):
      site = Woods(self, site_image)
      site.location = Vector2(random.randint(0,w), random.randint(0,h))
      self.add_entity(site)

    for animal_no in xrange(3):
      animal = Animal(self, animal_image)
      animal.location = Vector2(random.randint(0,w), random.randint(0,h))
      animal.brain.set_state("exploring")
      self.add_entity(animal)

    for human_name in ['Bob', 'Mary', 'Paula', 'Ariel', 'Moore']:
      human = Human(self, human_image, human_name)
      human.location = Vector2(random.randint(0,w), random.randint(0,h))
      human.brain.set_state("idle")
      self.add_entity(human)

class Perception(World):
  def __init__(self, animal):
    SCREEN_SIZE=(100, 60)
    #perception_size = (self.animal.sightrange)
    World.__init__(self, SCREEN_SIZE)
    self.animal = animal
    self.possible_targets = []

  def am_attacked(self):
    if self.am_seeked_by() == None:
      return False
    return True

  def am_seeked_by(self):
    for entity in self.entities.itervalues():
      different = entity.typestring != self.animal.typestring
      aggressive = entity.appearance == "aggressive"
      if entity != self and different and aggressive:
	return entity
    return None

  def percieve(self):
    self.entities = {}
    entity_names = []
    self.possible_targets = []
    for entity in self.animal.world.entities.itervalues():
      if self.percieves_entity(entity):
	self.add_entity(entity)
	entity_names.append(entity.name)
	if entity.typestring != self.animal.typestring and entity.alive:
	  self.possible_targets.append(entity)
    return entity_names
    #self.percieved_time = time_of_day

  def setmood(self, being):
    if being.hunger <= 2:
      being.mood = Mood("content")
    if being.hunger >= 12:
      being.mood = Mood("hungry")
    for other in being.percieved_objects:
      if other.appearance.name == "aggressive" and other.name != being.name:
	being.interrupted = True
	being.percieved_threats.append(other)
	if being.personality.name == "aggressive":
	  being.mood = Mood("aggressive")
	else:
	  being.mood = Mood("in fear")

  def percieves_entity(self, entity):
    if self.animal.location.get_distance_to(entity.location) <= 50.:
      return True
    else:
      return False

class GameEntity(object):
  def __init__(self, world, name, image):
    self.world = world
    self.name = name
    self.image = image
    self.state_icon = None
    self.location = Vector2(0,0)
    self.destination = Vector2(0,0)
    self.speed = 0
    self.brain = StateMachine(self)
    self.perception = Perception(self)
    self.id = 0
    self.indicated = False
    self.appearance = ""
    self.alive = False
    self.attack_cooldown = 200
    self.attack_cooldown_timer = 0

  def __str__(self):
    return self.name + " " + str((round(self.location.x), round(self.location.y)))

  def description_list(self):
    return [self.__str__()]

  def render(self, surface):
    x = self.location.x + self.world.camera_x
    y = self.location.y + self.world.camera_y
    w, h = self.image.get_size()
    surface.blit(self.image, (x-w/2, y-h/2))

    if self.state_icon:
      surface.blit(self.state_icon, (x-w , y-h))

  def process(self, time_passed):

    self.perception.percieve()
    self.brain.think()
    
    if self.attack_cooldown_timer > 0:
      self.attack_cooldown_timer -= time_passed * 100
    if self.speed > 0 and self.location != self.destination:
      vec_to_destination = self.destination - self.location
      distance_to_destination = vec_to_destination.get_magnitude()
      heading = vec_to_destination.normalize()
      travel_distance = min(distance_to_destination, time_passed * self.speed)
      self.location += heading * travel_distance

class Animal(GameEntity):
  def __init__(self, world, image, *name):
    GameEntity.__init__(self, world, "animal", image)
    exploring_state = AnimalStateExploring(self)
    seeking_state = AnimalStateSeeking(self)
    going_home_state = AnimalStateGoingHome(self)
    hunting_state = AnimalStateHunting(self)
    dead_state = AnimalStateDead(self)
    idle_state = AnimalStateIdle(self)

    self.brain.add_state(exploring_state)
    self.brain.add_state(seeking_state)
    self.brain.add_state(going_home_state)
    self.brain.add_state(hunting_state)
    self.brain.add_state(dead_state)
    self.brain.add_state(idle_state)

    self.mood = "content"
    self.appearance = "calm"
    self.home = Vector2(10,10)
    self.carried = {}
    self.carry_image = None
    self.alive = True
    self.normal_speed = 80

    self.typestring = "animal"

    self.target = None

    self.attack_modifier = 1
    self.attack_damage_dice_type = 6
    self.attack_damage_dice_count = 1
    self.attack_damage_plus = 0
    self.attack_cooldown = 200
    self.attack_target = None
    self.defence = 10
    self.hp = self.maxhp = 10

  def render(self, surface):
    GameEntity.render(self, surface)

    #------------- draw health bar -------------
    x = self.location.x + self.world.camera_x
    y = self.location.y + self.world.camera_y
    w, h = self.image.get_size()
    bar_x = x - w/2
    bar_y = y + h/2
    surface.fill( (255, 0, 0), (bar_x, bar_y, w, 3))
    surface.fill( (0, 255, 0), (bar_x, bar_y, w * self.hp / self.maxhp, 3))

    if self.carry_image:
      surface.blit(self.carry_image, (x-w , y -h))
  
  def __str__(self):
    return self.name + " " + str((round(self.location.x), round(self.location.y))) + " state: " + self.brain.active_state.name

  def description_list(self):
    if self.target == None:
      target_name = "None"
    else:
      target_name = self.target.name
    string0 = self.__str__()
    string1 = str(self.hp) + "/" + str(self.maxhp) + " hp "
    string2 = "State: " + self.brain.active_state.name + " Target: " + target_name
    string3 = "carried: " + str(self.carried)
    string4 = "percieves: " + str(self.perception.percieve())
    return [string0, string1, string2, string3, string4]

class Human(Animal):
  def __init__(self, world, image, name):
    Animal.__init__(self, world, image, name)
    self.name = name
    self.typestring = "human"

    self.defence = 17 #testzwecke
    self.hp = self.maxhp = 20

    self.projectmachine = ProjectMachine()
    working_state = HumanStateWorking(self)
    going_to_work_state = HumanStateGoingToWork(self)
    idle_state = HumanStateIdle(self)

    build_project = BuildProject(self, Farm(self.world))
    finding_constr_place_state = HumanStateFindingConstructionPlace(self)
    constructing_state = HumanStateConstructing(self)
    bringing_ressources_state=HumanStateBringingRessources(self)

    self.brain.add_state(working_state)
    self.brain.add_state(going_to_work_state)
    self.brain.add_state(idle_state)

    self.projectmachine.add_project(build_project)
    self.brain.add_state(finding_constr_place_state)
    self.brain.add_state(constructing_state)
    self.brain.add_state(bringing_ressources_state)

    self.home = Vector2(100,100)

  def __str__(self):
    return self.name + " " + str((round(self.location.x), round(self.location.y))) + " state: " + self.brain.active_state.name

  def pick_up_ressource(self, ressource, site):
    self.carried[ressource] = 1
    site.ressources[ressource] -= 1
    self.carry_image = pygame.image.load("pics/paket.png").convert_alpha()

  def drop_all_ressources(self, site):
    for ressource in self.carried.iterkeys():
      site.increase_ressource(ressource,1)
    self.carried = {}
    self.carry_image = None

class Site(GameEntity):
  def __init__(self, world, image):
    GameEntity.__init__(self, world, "site", image)
    self.typestring = "site"
    self.finished = True
    self.completion = 100
    self.produced_ressources = ""
    self.ressources ={}
    self.production_delay = 0.0

  def __str__(self):
    return self.name + " " + str((round(self.location.x), round(self.location.y))) + " Ressources: " + str(self.ressources)

  def description_list(self):
    string0 = self.__str__()
    string1 = "Completion: " + str(self.completion) + "/" + str(100)
    string2 = "Ressources at Site: " + str(self.ressources)
    return [string0, string1, string2]

  def check_ressource(self, ressource):
    if self.ressources.keys().count(ressource) != 0:
      return self.ressources[ressource]
    else:
      return 0

  def increase_ressource(self, ressource, value):
    if self.ressources.keys().count(ressource) == 0:
      self.ressources[ressource] = 0
    self.ressources[ressource] += value

class Farm(Site):
  def __init__(self, world):
    self.image = pygame.image.load("pics/ziel.png").convert_alpha()
    Site.__init__(self, world, self.image)
    self.produced_ressources = "wheat"
    self.name = "Farm"
    self.production_delay = 200
    self.needed_ressources = {"lumber":10, "wheat":2}
    self.finished = True

class Woods(Site):
  def __init__(self, world, image):
    Site.__init__(self, world, image)
    self.produced_ressources = "lumber"
    self.ressources ={"lumber":2}
    self.image = pygame.image.load("pics/woods.png").convert_alpha()
    self.production_delay = 300
    self.finished = True
    self.name = "Woods"