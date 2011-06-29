# -*- coding: utf-8 -*-

import dorflib, pygame

class ProjectMachine(object):
  def __init__(self):
    self.projects = {}
    self.active_project = None

  def add_project(self, project):
    self.projects[project.name] = project

  def set_project(self, new_project_name):
    if self.active_project is not None:
      self.active_project.exit_actions()
    self.active_project = self.projects[new_project_name]
    self.active_project.entry_actions()

class Project(object):
  def __init__(self, name):
    self.needed_ressources = {}
    self.name = name
    self.site = None

  def entry_actions(self):
    pass

  def exit_actions(self):
    pass

  def add_needed_ressource(self):
    pass

class BuildProject(Project):
  def __init__(self, human, building):
    Project.__init__(self, "build project")
    picfolder="pics/"
    self.site_image = pygame.image.load(picfolder + "construction_site.png").convert_alpha()
    self.human = human
    self.building = building
    self.site = None
    self.ressource_sites = []
    self.ressource_producing_sites = []
    self.next_ressource = ""

  def entry_actions(self):
    self.needed_actions = ["finding construction place", "bringing ressources", "constructing"]
    self.needed_ressources = self.building.needed_ressources

  def ressources_delivered(self):
    if not self.site == None:
      enough_ressources = True
      for ressource in self.needed_ressources.iterkeys():
	if self.needed_ressources[ressource] > self.site.check_ressource(ressource):
	  enough_ressources = False
      return enough_ressources

  def set_construction_site(self, destination):
    self.site = dorflib.Site(self.human.world, self.site_image)
    self.site.location = self.human.location
    self.site.name = "construction site"
    self.site.completion = 0
    self.site.finished = False
    self.human.world.add_entity_cache.append(self.site)
    del self.needed_actions[0]

  def finish_building(self):
    pass

  def set_next_ressource(self):
    for ressource in self.needed_ressources.iterkeys():
      if self.needed_ressources[ressource] > self.site.check_ressource(ressource):
	if self.ressource_available(ressource):
	  self.next_ressource = ressource

  def define_ressource_sites(self, ressource):
    for site in self.human.world.entities_of_type("site"):
      if site.check_ressource(ressource) >= 1 and site != self.site and site.finished:
	self.ressource_sites.append(site)

  def set_ressource_producing_sites(self):
    for site in self.human.world.entities_of_type("site"):
      if site.produced_ressources in self.needed_ressources:
	self.ressource_producing_sites.append(site)

  def ressource_available(self, ressource):
    added_ressources = 0
    for site in self.human.world.entities_of_type("site"):
      if ressource in site.ressources:
	added_ressources += site.ressources[ressource]
    if added_ressources >= 5:
      return True
    else:
      return False