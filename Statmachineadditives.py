# -*- coding: utf-8 -*-
  def define_state(self, being, time_of_day, dorfactive):
    if being.present_project.name == "go to sleep":
      being.go_to(being.home)
      if being.arrived():
	being.state = "sleeping"
	being.mood = Mood("content")
    elif being.present_project.name == "hide":
      being.go_to(being.home)
      being.mood.cooldown = 50
      if being.arrived():
	being.state = "hiding"
    elif being.present_project.name == "working":
      being.go_to(being.workplace)
      if being.arrived():
	being.state = "working"
    elif being.present_project.name == "get food":
       being.go_to(being.home)
       if being.arrived():
	 being.state = "eating"
    elif being.present_project.name == "wandering" and being.arrived():
      being.go_to(random.choice(dorfactive.locdict.values()))
    elif being.present_project.name == "build windmill":
      being.go_to(Vector2.Vector2(*being.present_project.destination))
      if being.arrived():
	being.state = "constructing windmill"
    elif being.present_project.name == "attack threat":
      if len(being.percieved_threats) >= 1:
	being.attack_target = being.percieved_threats[random.randint(0,len(being.percieved_threats)-1)]
      being.go_to(being.attack_target)
      if being.arrived():
	being.state = "fighting"

  #valid next_actions as planned: go_to, find, get, persuade, pursue, ...
  def decide_present_project(self, being, time_of_day, dorfactive):
    if time_of_day == "night" and len(being.percieved_threats) == 0:
      being.present_project = Project("go to sleep")
    elif time_of_day == "day" and being.mood.name == "content":
      if isinstance(being, dorflib.Person):
	if being.profession == "Lumberjack" and dorfactive.locdict['Woods'].product_count >= 20:
	  being.present_project = Project("build windmill")
	  being.present_project.destination = (dorfactive.windmill_x, dorfactive.windmill_y)
	elif being.profession == "soldier":
	  being.present_project = Project("wandering")
	else:
	  being.present_project = Project("working")
      else:
	being.present_project = Project("wandering")
    elif being.mood.name == "in fear":
      being.present_project = Project("hide")
    elif being.mood.name == "hungry":
      being.present_project = Project("get food")
    elif being.mood.name == "aggressive":
      being.present_project = Project("attack threat")


class HumanStateWorking(State):
  def __init__(self, human):
    State.__init__(self, "working")
    self.human = human
  def do_actions(self):
    self.human.state = "working"