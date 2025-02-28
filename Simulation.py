# simulation space W*L
# random object creation in simulation space
# randomize light ray
# render triangles

import numpy as np
import pygame as pg
from OpenGL.GL import *
from Subspace import *

class App:
    
    def __init__ (self):

        pg.init()
        pg.display.set_mode((300,200), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        glClearColor(0,0,0,1)
        self.mainLoop()

        

    def mainLoop(self):

        running = True
        while (running):
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            glClear(GL_COLOR_BUFFER_BIT)



            pg.display.flip()

            self.clock.tick(60)
        self.quit()

    def quit(self):

        pg.QUIT()

class Triangle:

    def __init__ (self):
        pass

if __name__ == "__main__":
    myApp = App()
    myApp.mainLoop()
    myApp.quit()

class ray:
    def __init__(self, origin, direction):
        self.origin = np.array(origin)