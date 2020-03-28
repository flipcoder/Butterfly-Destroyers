from random import randint, choice

from glm import vec2, vec3, ivec2
import pygame
import random

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS
from game.util import ncolor, random_rgb
from game.constants import *


class Rain(Entity):
    def __init__(self, app, scene, pos: vec3, z_vel: float, **kwargs):

        super().__init__(app, scene, None, position=pos, **kwargs)

        self._surface = self.app.load(
            "RAIN", lambda: pygame.Surface(ivec2(2, 24)).convert()
        ).copy()
        self._surface.fill((255, 255, 255))
        self._surface.set_alpha(50)

        self.velocity = vec3(0, -1000, 1000 + z_vel)

    def render(self, camera):
        return super().render(camera, scale=False)