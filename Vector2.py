# -*- coding: utf-8 -*-
import math

class Vector2(object):

  def __init__(self, x=0.0, y=0.0):
    self.x = x
    self.y = y

  def __str__(self):
    return "(%s, %s)"%(self.x, self.y)

  @staticmethod
  def from_points(P1, P2):
    return Vector2( P2.x - P1.x, P2.y - P1.y )

  def get_magnitude(self):
    return math.sqrt( self.x**2 + self.y**2 )

  def normalize(self):
    magnitude = self.get_magnitude()
    if magnitude != 0:
      self.x /= magnitude
      self.y /= magnitude
      return Vector2(self.x, self.y)
    else:
      self.x = 0
      self.y = 0
      return Vector2(0,0)

  def __add__(self, rhs):
    return Vector2(self.x + rhs.x, self.y + rhs.y)

  def __sub__(self, rhs):
    return Vector2(self.x - rhs.x, self.y - rhs.y)

  def __neg__(self):
    return Vector2(-self.x, -self.y)

  def __mul__(self, scalar):
    return Vector2(self.x * scalar, self.y * scalar)

  def __div__(self, scalar):
    return Vector2(self.x / scalar, self.y / scalar)

  def get_distance_to(self, position):
    return Vector2.from_points(self, position).get_magnitude()
