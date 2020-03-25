#!/usr/bin/python
import pygame
from glm import ivec2, vec2

from game.base.signal import Signal

from game.states.game import Game
from game.states.intro import Intro
import time


class App:

    STATES = {"intro": Intro, "game": Game}
    MAX_KEYS = 512

    def __init__(self, initial_state):
        """
        The main beginning of our application.
        Initializes pygame and the initial state.
        """

        pygame.init()

        self.size = ivec2(1920, 1080) / 2
        """Display size"""
        self.cache = {}
        """Resources with filenames as keys"""
        self.screen = pygame.display.set_mode(self.size)
        self.on_event = Signal()
        self.quit = False
        self.clock = pygame.time.Clock()
        self.time = 0
        self.dirty = True
        self.keys = [False] * self.MAX_KEYS

        self._state = None
        self.last_state = None
        self.next_state = initial_state
        self.process_state_change()

    def load(self, filename, resource_func):
        """
        Attempt to load a resource from the cache, otherwise, loads it
        :param resource_func: a function that loads the resource if its
            not already available in the cache
        """
        if filename not in self.cache:
            r = self.cache[filename] = resource_func()
            return r
        return self.cache[filename]

    def load_img(self, filename):
        """Load the image at the given path in a pygame surface. Results are cached"""
        return self.load(filename, lambda: pygame.image.load(filename))

    # def pend(self):

    #     self.dirty = True

    def run(self):
        """
        Main game loop.

        Runs until the `quit` flag is set
        Runs update(dt) and render() of the current game state (default: Game)
        """

        last_t = time.time_ns()
        accum = 0
        self.fps = 0
        frames = 0
        while (not self.quit) and self.state:

            cur_t = time.time_ns()
            dt = (cur_t - last_t) / (1000 * 1000 * 1000)
            last_t = cur_t
            accum += dt
            frames += 1
            if accum > 1:
                self.fps = frames
                frames = 0
                accum -= 1
            dt = self.clock.tick(0) / 1000
            # print(t)
            time.sleep(0.0001)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                elif event.type == pygame.KEYDOWN:
                    self.keys[event.key] = True
                elif event.type == pygame.KEYDOWN:
                    self.keys[event.key] = False
                self.on_event(event)

            if self.state is None:
                break

            if self.update(dt) is False:
                break

            if self.render() is False:
                break

    def add_event_listener(self, obj):
        slot = self.on_event.connect(obj.event, weak=True)
        obj.slots.append(slot)
        return slot

    def update(self, dt):
        """
        Called every frame to update our game logic
        :param dt: time since last frame in seconds
        :return: returns False to quit gameloop
        """

        if not self.state:
            return False

        if self.next_state:
            self.process_state_change()

        self.state.update(dt)

    def render(self):
        """
        Called every frame to render our game state and update pygame display
        :return: returns False to quit gameloop
        """

        # if not self.dirty:
        #     return
        # self.dirty = False

        if self.state is None:
            return False

        self.state.render()

        pygame.display.update()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, s):
        """
        Schedule state change on next frame
        """
        self.next_state = s

    def process_state_change(self):
        """
        Process pending state changes
        """
        if self.next_state:
            self._state = self.STATES[self.next_state.lower()](self)
        self.next_state = None
