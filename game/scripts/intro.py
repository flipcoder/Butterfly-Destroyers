#!/usr/bin/env python
import pygame.mixer


def script(app, scene):
    terminal = app.state.terminal

    scene.sky_color = "black"
    typ = pygame.mixer.Sound("data/sounds/type.wav")

    msg = "Welcome to Butterfly Destroyers!"
    for i in range(len(msg)):
        terminal.write(msg[i], (i, 0), "red")
        typ.play()
        yield scene.sleep(0.1)

    while True:
        terminal.write("Press any key to continue", (0, 2), "white")
        yield scene.sleep(0.2)
        terminal.clear(2)
        yield scene.sleep(0.2)

        keys = app.keys()
        if any(keys):
            break

    scene.sky_color = "white"
    terminal.clear()
