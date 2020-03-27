import pygame
from glm import vec3, normalize

from game.base.entity import Entity
from game.constants import BULLET_OFFSET, BULLET_IMAGE_PATH
from game.entities.bullet import Bullet


class Weapon(Entity):
    def __init__(self, player, ammo, speed, damage, app, scene):
        """
        A generic weapon.

        :param player: The player holding the weapon
        :param ammo: Max ammunition
        :param speed: bullets per second
        :param damage: damage per bullet
        """
        super().__init__(app, scene, parent=player)
        self.ammo = ammo  # current ammo
        self.cooldown = 1 / speed
        self.damage = damage

        self.last_fire = float("inf")

    def update(self, dt):
        super().update(dt)

        self.last_fire += dt

    def get_bullets(self, aim):
        raise NotImplementedError

    def fire(self, aim):
        """Fire if it can"""

        if self.last_fire < self.cooldown:
            return False
        if self.ammo == 0:
            return False

        for bullet in self.get_bullets(aim):
            self.scene.add(bullet)

        self.ammo -= 1
        self.last_fire = 0

        return True


class Pistol(Weapon):
    color = "yellow"
    letter = "P"
    max_ammo = -1

    def __init__(self, app, scene, player):
        super(Pistol, self).__init__(player, self.max_ammo, 3, 1, app, scene)

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        yield Bullet(
            self.app,
            self.scene,
            self.parent,
            start,
            direction,
            self.damage,
            BULLET_IMAGE_PATH,
        )


class MachineGun(Weapon):
    color = "orange"
    letter = "M"
    max_ammo = 25

    def __init__(self, app, scene, player):
        super(MachineGun, self).__init__(player, self.max_ammo, 6, 1, app, scene)

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start1 = camera.rel_to_world(BULLET_OFFSET + vec3(8, 0, 0))
        start2 = camera.rel_to_world(BULLET_OFFSET + vec3(-8, 0, 0))

        for start in (start1, start2):
            yield Bullet(
                self.app,
                self.scene,
                self.parent,
                start,
                aim - start,
                self.damage,
                BULLET_IMAGE_PATH,
            )


class Laser(Bullet):
    def __init__(self, app, scene, parent, position, direction, length, color, damage):
        super().__init__(app, scene, parent, position, direction, damage)
        self.color = pygame.Color(color)
        self.size.z = length

    def render(self, camera):
        p1 = camera.world_to_screen(self.position)
        p2 = camera.world_to_screen(
            self.position + normalize(self.velocity) * self.size.z
        )

        pygame.draw.line(self.app.screen, self.color, p1, p2, 4)


class LaserGun(Weapon):
    letter = "L"
    color = "red"
    max_ammo = 20

    def __init__(self, app, scene, player):
        super(LaserGun, self).__init__(player, self.max_ammo, 2, 2, app, scene)

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        for x in range(5):
            yield Laser(
                self.app,
                self.scene,
                self.parent,
                start,
                direction,
                100,
                "red",
                self.damage / 5,
            )


WEAPONS = [Pistol, MachineGun, LaserGun]
