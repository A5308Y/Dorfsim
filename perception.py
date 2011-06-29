# -*- coding: utf-8 -*-
import dorflib, Vector2

class Perception(World):
  def __init__(self, human):
    self.human = human

  def percieve(self):
    pass

  def is_interrupted(self):
    pass

  def set_perception(self):
    for entity in self.human.world.enitities.itervalues():
      if self.percieves_entity(entity):
	self.add_entity(entity)
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
    if self.human.location.get_distance(entity.location) <= 50.:
      return True
    else:
      return False