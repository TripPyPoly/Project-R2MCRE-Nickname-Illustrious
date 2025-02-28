import numpy as np
import pygame as pg
from OpenGL.GL import *
from shapely.geometry import Point, Polygon

class App:
    def __init__(self):
        pg.init()
        pg.display.set_mode((500, 500), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        
        glClearColor(0, 0, 0, 1)
        glOrtho(-10, 10, -10, 10, -1, 1)  # Orthographic projection
        
        self.square = Square(side_length=6, center=(0, 0), rotation=30)
        self.shadow_renderer = ShadowRenderer(self.square)
        
        self.mainLoop()
    
    def mainLoop(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            glClear(GL_COLOR_BUFFER_BIT)
            
            # Draw square
            self.square.draw()
            
            # Render shadow
            self.shadow_renderer.update()
            self.shadow_renderer.render()
            
            pg.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        self.quit()
    
    def quit(self):
        pg.quit()

class Square:
    def __init__(self, side_length=6, center=(0, 0), rotation=30):
        self.side_length = side_length
        self.center = np.array(center)
        self.rotation = np.radians(rotation)
        self.vertices = self.generate_vertices()
        self.polygon = Polygon(self.vertices)  # Create a shapely polygon for collision detection

    def generate_vertices(self):
        """Generate square vertices given side length, center, and rotation."""
        half_side = self.side_length / 2
        square = np.array([
            [-half_side, -half_side],
            [ half_side, -half_side],
            [ half_side,  half_side],
            [-half_side,  half_side]
        ])
        
        # Rotation matrix
        rotation_matrix = np.array([
            [np.cos(self.rotation), -np.sin(self.rotation)],
            [np.sin(self.rotation), np.cos(self.rotation)]
        ])
        
        # Apply rotation and translation
        rotated_square = (square @ rotation_matrix.T) + self.center
        return rotated_square

    def draw(self):
        """Draw the square using OpenGL."""
        glColor3f(1, 1, 1)  # White color
        glBegin(GL_LINE_LOOP)
        for vertex in self.vertices:
            glVertex2f(vertex[0], vertex[1])
        glEnd()

class ShadowRenderer:
    def __init__(self, square, num_points=1000):
        self.square = square
        self.num_points = num_points
        self.points = np.random.uniform(-10, 10, (self.num_points, 2))
    
    def update(self):
        """Update points each frame to simulate real-time randomization."""
        self.points = np.random.uniform(-10, 10, (self.num_points, 2))
    
    def render(self):
        """Render shadow by grouping points into triangles."""
        in_square = []
        out_square = []

        for point in self.points:
            shapely_point = Point(point[0], point[1])
            if self.square.polygon.contains(shapely_point):
                in_square.append(point)
            else:
                out_square.append(point)

        glColor3f(0.3, 0.3, 0.3)  # Darker color for outside points
        self.draw_triangles(out_square)
        
        glColor3f(0.6, 0.6, 0.6)  # Lighter color for inside points
        self.draw_triangles(in_square)

    def draw_triangles(self, points):
        """Draw points as connected triangles with random point selection."""
        if len(points) < 3:
            return
        
        glBegin(GL_TRIANGLES)
        for i in range(len(points)):
            # Select 2 random indices (distinct) from the points list using numpy
            random_indices = np.random.choice(len(points), size=2, replace=False)
        
            # Retrieve the points from the random indices
            random_point1 = points[random_indices[0]]
            random_point2 = points[random_indices[1]]
        
            # Render the triangle with the current point and two random points
            glVertex2f(points[i][0], points[i][1])
            glVertex2f(random_point1[0], random_point1[1])
            glVertex2f(random_point2[0], random_point2[1])
        
        glEnd()

if __name__ == "__main__":
    myApp = App()
    myApp.mainLoop()
    myApp.quit()