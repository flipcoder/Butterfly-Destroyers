#!/usr/bin/python
from glm import vec3, sign

from game.base.entity import Entity
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.butterfly import Butterfly


class Player(Entity):
    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, filename=SHIP_IMAGE_PATH)

        self.score = 0

        self.dirkeys = [
            # directions
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]

        self.actionkeys = [pygame.K_RETURN, pygame.K_SPACE]
        self.dir = [False] * len(self.dirkeys)

        self.position = vec3(0, 0, 0)
        self.speed = vec3(speed)

        self.solid = True

    def collision(self, other, dt):
        if isinstance(other, Butterfly):
            self.score += 1
            other.explode()

    def action(self, btn):

        # Assuming state is Game
        camera = self.app.state.camera
        aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start
        self.scene.add(Bullet(self.app, self.scene, self, start, direction))

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.dirkeys):
                if key == event.key:
                    self.dir[i] = event.type == pygame.KEYDOWN
            for i, key in enumerate(self.actionkeys):
                if key == event.key:
                    if event.type == pygame.KEYDOWN:
                        self.action(0)

    def update(self, dt):

        self.velocity = (
            vec3(
                -self.dir[0] + self.dir[1],
                -self.dir[3] + self.dir[2],
                -1,  # always going forwards
            )
            * self.speed
        )

        super().update(dt)

    def render(self, camera):
        rect = self._surface.get_rect()
        rect.center = (self.app.size[0] / 2, self.app.size[1] * 0.8)

        direction = sign(self.velocity.xy)
        rect.center += direction * (10, -10)

        self.app.screen.blit(self._surface, rect)
