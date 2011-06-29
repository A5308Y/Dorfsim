# -*- coding: utf-8 -*-

import Vector2, random, dorflib, pygame
from Vector2 import *

class State(object):
  def __init__(self, name):
    self.name = name

  def do_actions(self):
    pass
  
  def check_conditions(self):
    pass

  def entry_actions(self):
    pass

  def exit_actions(self):
    pass

class StateMachine(object):
  def __init__(self, animal):
    self.states = {}
    self.active_state = None
    self.animal = animal
  
  def add_state(self, state):
    self.states[state.name] = state

  def think(self):
    if self.active_state is None:
      return
    self.active_state.do_actions()
    new_state_name = self.active_state.check_conditions()
    if new_state_name is not None:
      self.set_state(new_state_name)

  def set_state(self, new_state_name):
    if self.active_state is not None:
      self.active_state.exit_actions()
    self.active_state = self.states[new_state_name]
    self.active_state.entry_actions()

#-------------- DEFINED STATES --------------------

class AnimalStateIdle(State):
  def __init__(self, animal):
    State.__init__(self, "idle")
    self.animal = animal

  def check_conditions(self):
    return "exploring"

class AnimalStateExploring(State):
  def __init__(self, animal):
    State.__init__(self, "exploring")
    self.animal = animal

  def random_destination(self):
    w, h = self.animal.world.SCREEN_SIZE
    self.animal.destination = Vector2(random.randint(0,w), random.randint(0,h))

  def entry_actions(self):
    self.animal.speed = 80
    self.random_destination()

  def do_actions(self):
    if random.randint(1,20) == 1:
      self.random_destination()

  def check_conditions(self):
    if self.animal.perception.am_attacked():
      self.animal.target = self.animal.perception.am_seeked_by()
      return "hunting"

    if len(self.animal.perception.possible_targets) > 0:
      target = random.choice(self.animal.perception.possible_targets)
      if not target == None and target != self.animal:
	self.animal.target = target
	return "seeking"

class AnimalStateSeeking(State):
  def __init__(self, animal):
    State.__init__(self, "seeking")
    self.animal = animal
    self.target = None

  def entry_actions(self):
    self.animal.speed = 110
    self.target = self.animal.target
    self.animal.appearance = "aggressive"
    self.animal.destination = self.target.location

  def check_conditions(self):
    if self.animal.location.get_distance_to(self.animal.destination) <= 10:
      return "hunting"

  def do_actions(self):
    self.animal.destination = self.target.location

class AnimalStateGoingHome(State):
    def __init__(self, animal):
      State.__init__(self, "going home")
      self.animal = animal

    def entry_actions(self):
      self.animal.speed = 60
      self.animal.destination = self.animal.home

    def check_conditions(self):
      if self.animal.perception.am_attacked():
	self.animal.target = self.animal.perception.am_seeked_by()
	return "hunting"

class AnimalStateDelivering(State):
  pass

class AnimalStateDead(State):
  def __init__(self, animal):
    State.__init__(self, "dead")
    self.animal = animal

  def entry_actions(self):
    self.animal.speed = 0
    self.animal.appearance = "dead"
    self.animal.image = pygame.transform.flip(self.animal.image, 0, 1)
    print str(self.animal.name) + " died."
    self.animal.alive = False

class AnimalStateHunting(State):
  def __init__(self, animal):
    State.__init__(self, "hunting")
    self.animal = animal

  def entry_actions(self):
    self.animal.speed = 180
    self.target = self.animal.target
    self.animal.destination = self.target.location
    self.animal.apperance = "aggressive"
    self.animal.state_icon = pygame.image.load("pics/hunting.png")

  def do_actions(self):
    self.animal.destination = self.target.location
    if self.animal.location.get_distance_to(self.target.location) <= 5.0:
      if self.animal.attack_cooldown_timer <= 0:
	self.attack(self.target)
  
  def check_conditions(self):
    if not self.target.alive:
      return "idle"

  def exit_actions(self):
    self.animal.appearance = "calm"
    self.animal.target = None
    self.animal.speed = self.animal.normal_speed
    self.animal.state_icon = None

  def attack(self, target):
    self.animal.attack_cooldown_timer = self.animal.attack_cooldown
    damage = self.animal.attack_damage_plus
    if self.animal.location.get_distance_to(self.target.location) <= 5.0:
      if random.randint(1,20) + self.animal.attack_modifier >= self.target.defence:
	for i in range(self.animal.attack_damage_dice_count):
	  damage += random.randint(1,self.animal.attack_damage_dice_type)
	target.hp -= damage
	print self.animal.name + " hits " + target.name + " for " + str(damage) + " HP. (" + str(target.hp) + " HP left.) "
	if target.hp <= 0:
	  target.brain.set_state("dead")
      else:
	print self.animal.name + " misses " + target.name
    else:
      print "target out of range."

#-------------------- HUMAN STATES ---------------------------
#------------------ Project States -------------------------

class HumanStateWorking(State):
  def __init__(self, human):
    State.__init__(self, "working")
    self.human = human
    self.production_increase_timer = 0

  def entry_actions(self):
    self.human.speed = 0
    self.human.state_icon = pygame.image.load("pics/working.png").convert_alpha()
    #self.human.mood = "annoyed"
    self.production_increase_timer = self.human.workplace.production_delay
    self.product = self.human.workplace.produced_ressources

  def do_actions(self):
    self.production_increase_timer -= self.human.world.time_passed_seconds * 100
    if self.production_increase_timer <= 0:
      self.production_increase_timer = self.human.workplace.production_delay
      self.human.workplace.increase_ressource(self.product, 1)

  def check_conditions(self):
    if self.human.perception.am_attacked():
      self.human.target = self.human.perception.am_seeked_by()
      return "hunting"
    if self.human.workplace.check_ressource(self.product) >= 5:
      return "idle"

  def exit_actions(self):
    self.human.state_icon = None

class HumanStateGoingToWork(State):
  def __init__(self, human):
    State.__init__(self, "going to work")
    self.human = human

  def entry_actions(self):
    self.project = self.human.projectmachine.active_project
    self.human.speed = 100
    self.human.workplace = random.choice(self.human.world.entities_of_type("site"))

  def do_actions(self):
    if self.project != None:
      if self.project.name == "build project":
	self.project.set_ressource_producing_sites()
	sites = self.project.ressource_producing_sites
	world = self.human.world
	self.human.workplace = world.closest_entity_in_list(self.human, sites)
    self.human.destination = self.human.workplace.location

  def check_conditions(self):
    if self.human.perception.am_attacked():
      self.human.target = self.human.perception.am_seeked_by()
      return "hunting"
    if self.human.mood == "content" and self.human.location.get_distance_to(self.human.destination) <= 10:
      if self.project != None:
	for ressource in self.human.projectmachine.active_project.needed_ressources.iterkeys():
	  if self.human.workplace.check_ressource(ressource) >= 1 :
	    return "bringing ressources"
      return "working"

class HumanStateIdle(State):
  def __init__(self, human):
    State.__init__(self, "idle")
    self.human = human

  def entry_actions(self):
    self.project = self.human.projectmachine.active_project

  def check_conditions(self):
    if self.human.perception.am_attacked():
      self.human.target = self.human.perception.am_seeked_by()
      return "hunting"
    if self.human.mood == "content":
      if self.project == None:
	if random.randint(1,100) <= 50:
	  self.human.projectmachine.set_project("build project")
      if self.human.projectmachine.active_project != None:
	return self.human.projectmachine.active_project.needed_actions[0]

  #def decide_project #!!!
  #  pass

class HumanStateFindingConstructionPlace(State):
  def __init__(self, human):
    State.__init__(self, "finding construction place")
    self.human = human

  def random_destination(self):
    w, h = self.human.world.SCREEN_SIZE
    self.human.destination = Vector2(random.randint(0,w), random.randint(0,h))

  def entry_actions(self):
    self.human.speed = 80
    self.random_destination()
    self.project = self.human.projectmachine.active_project
    self.site = self.project.site

  def check_conditions(self):
    if self.human.perception.am_attacked():
      self.human.target = self.human.perception.am_seeked_by()
      return "hunting"
    if self.human.location.get_distance_to(self.human.destination) <= 1.0:
      self.project.set_construction_site(self.human.destination)
      return "constructing"

class HumanStateConstructing(State):
  def __init__(self, human):
    State.__init__(self, "constructing")
    self.human = human

  def entry_actions(self):
    self.project = self.human.projectmachine.active_project
    self.site = self.project.site
    self.human.destination = self.site.location

  def do_actions(self):
    arrived = self.human.location.get_distance_to(self.human.destination) <= 1.0
    if arrived and self.project.ressources_delivered():
      self.site.completion += 0.02 * self.human.world.time_passed
    if self.site.completion >= 100:
      self.site.completion = 100
      self.site.finished = True
      self.human.projectmachine.active_project = None

  def check_conditions(self):
    if self.human.perception.am_attacked():
      self.human.target = self.human.perception.am_seeked_by()
      return "hunting"
    if self.site.finished:
      self.site.ressources = {} # muss auch noch anders
      return "going to work"
    arrived = self.human.location.get_distance_to(self.human.destination) <= 1.0
    if arrived and not self.project.ressources_delivered():
      return "bringing ressources"

class HumanStateBringingRessources(State):
  def __init__(self, human):
    State.__init__(self, "bringing ressources")
    self.human = human

  def entry_actions(self):
    self.human.speed = self.human.normal_speed
    self.project = self.human.projectmachine.active_project
    self.site = self.project.site
    self.ressource_site = None

    self.choose_ressource_site()
    #if len(self.human.carried) == 0:
      #self.human.destination = self.ressource_site.location
    #else:
      #self.human.destination = self.site.location

  def choose_ressource_site(self):
    self.project.set_next_ressource()
    self.project.define_ressource_sites(self.project.next_ressource)
    self.ressource_site = self.human.world.closest_entity_in_list(self.human, self.project.ressource_sites)

  def do_actions(self):
    distance_to_site = self.human.location.get_distance_to(self.site.location)
    
    if not self.ressource_site == None:
      if self.ressource_site.check_ressource(self.project.next_ressource) <= 0:
	self.project.ressource_sites.remove(self.ressource_site)
	self.choose_ressource_site()

    if len(self.human.carried) >= 1:
      self.human.destination = self.site.location
      if distance_to_site <= 1:
	self.human.drop_all_ressources(self.site)

    if len(self.human.carried) <= 0:
      self.choose_ressource_site()
      if not self.ressource_site == None:
	distance_to_ressource = self.human.location.get_distance_to(self.ressource_site.location)
	self.human.destination = self.ressource_site.location
	if distance_to_ressource <= 1 and self.ressource_site.check_ressource(self.project.next_ressource) >= 1:
	  self.human.pick_up_ressource(self.project.next_ressource, self.ressource_site)

  def check_conditions(self):
    if self.human.perception.am_attacked():
      self.human.target = self.human.perception.am_seeked_by()
      return "hunting"
    if self.project.ressources_delivered():
      return "constructing"
    if len(self.human.carried) <= 0 and len(self.project.ressource_sites) == 0:
      return "going to work"

#not implemented
class HumanStateFindingRessources(State):
  def __init__(self, human):
    State.__init__(self, "checking ressources")
    self.human = human

  def entry_actions(self):
    ressource_name = self.human.project_machine.active_project.needed_ressource_name
    ressource_count = self.human.project_machine.active_project.needed_ressource_count

  def check_conditions(self):
    if destination.ressource_name < destination.ressource_count[ressource_name]:
      return "bringing ressources"