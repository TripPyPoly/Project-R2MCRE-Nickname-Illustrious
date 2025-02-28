import numpy as np
import pygame as pg
from OpenGL.GL import *
from shapely.geometry import LineString, Point


class App:
    def __init__(self):
        pg.init()
        pg.display.set_mode((500, 500), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        glClearColor(0, 0, 0, 1)
        glOrtho(-10, 10, -10, 10, -1, 1)  # Orthographic projection

        self.square = Square(side_length=6, center=(0, 0), rotation=30)
        self.ray_tracer = MonteCarloRayTracer(self.square)

        self.frame_counter = 0  # To slow down ray spawning

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

            # Add a new ray every few frames
            if self.frame_counter % 10 == 0:  # Slow down ray spawning
                self.ray_tracer.add_ray()

            # Draw rays and triangles
            self.ray_tracer.draw_rays()
            self.ray_tracer.draw_triangles()

            pg.display.flip()
            self.clock.tick(60)  # 60 FPS
            self.frame_counter += 1

        self.quit()

    def quit(self):
        pg.quit()


class Square:
    def __init__(self, side_length=6, center=(0, 0), rotation=30):
        self.side_length = side_length
        self.center = np.array(center)
        self.rotation = np.radians(rotation)
        self.vertices = self.generate_vertices()
        self.edges = self.get_edges()

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

    def get_edges(self):
        """Return Shapely LineStrings for square edges."""
        return [
            LineString([self.vertices[i], self.vertices[(i + 1) % 4]])
            for i in range(4)
        ]

    def draw(self):
        """Draw the square using OpenGL."""
        glColor3f(1, 1, 1)  # White color
        glBegin(GL_LINE_LOOP)
        for vertex in self.vertices:
            glVertex2f(vertex[0], vertex[1])
        glEnd()


class MonteCarloRayTracer:
    def __init__(self, square):
        self.square = square
        self.rays = []  # Store all previous rays
        self.first_intersections = []  # Store rays that hit the square first
        self.second_intersections = []  # Store intersections with the backboard
        self.triangles = []  # Store generated triangles

    def generate_parallel_ray(self):
        """Generate a parallel ray that moves exactly rightward."""
        origin_x = -10  # Start from the far left
        origin_y = np.random.uniform(-10, 10)  # Random y-position
        end_x = 10  # Extend far right
        end_y = origin_y  # Same y-value for perfect parallelism

        return LineString([(origin_x, origin_y), (end_x, end_y)])

    def add_ray(self):
        """Generate a new ray, find intersections, and store results."""
        ray = self.generate_parallel_ray()
        self.rays.append(ray)

        # Find the closest square intersection
        closest_intersection = None
        min_distance = float("inf")

        for edge in self.square.get_edges():
            intersection = ray.intersection(edge)
            if intersection and not intersection.is_empty:
                if isinstance(intersection, Point):
                    dist = abs(ray.coords[0][0] - intersection.x)
                    if dist < min_distance:
                        closest_intersection = intersection
                        min_distance = dist

        # Find intersection with the right-side screen boundary (x = 10)
        right_wall = LineString([(10, -10), (10, 10)])
        right_intersection = ray.intersection(right_wall)

        if closest_intersection and isinstance(right_intersection, Point):
            # Store intersection points
            self.first_intersections.append((closest_intersection.x, closest_intersection.y))
            self.second_intersections.append((right_intersection.x, right_intersection.y))

            # If we have at least two first intersection points, form a triangle
            if len(self.first_intersections) >= 2:
                self.triangles.append([
                    self.first_intersections[-2],  # Previous first intersection
                    self.first_intersections[-1],  # Current first intersection
                    self.second_intersections[-2]  # Previous second intersection
                ])

    def draw_rays(self):
        """Draw the rays while keeping the incoming rays parallel."""
    
        # Green: Parallel rays going all the way across
        glColor3f(0, 0.2, 0)  # Green for incoming rays
        glBegin(GL_LINES)
        for ray in self.rays:
            glVertex2f(ray.coords[0][0], ray.coords[0][1])  # Start far left
            glVertex2f(ray.coords[1][0], ray.coords[1][1])  # End far right
        glEnd()

        # Purple: The segment from square intersection to backboard
        glColor3f(1, 0, 1)  # Purple for rays from square to the backboard
        glBegin(GL_LINES)
        for i in range(len(self.second_intersections)):
            glVertex2f(self.first_intersections[i][0], self.first_intersections[i][1])
            glVertex2f(self.second_intersections[i][0], self.second_intersections[i][1])
        glEnd()

        # Red: Intersection points (square + backboard)
        glColor3f(1, 0, 0)  
        glPointSize(5)
        glBegin(GL_POINTS)
        for x, y in self.first_intersections + self.second_intersections:
            glVertex2f(x, y)
        glEnd()


    def draw_triangles(self):
        """Draws shaded triangles to fully fill the background behind the square."""
        glColor3f(0.5, 0.5, 0.5)  # Gray shade for infill
        glBegin(GL_TRIANGLES)

        for i in range(len(self.first_intersections) - 1):
            # Points from two consecutive rays
            p1, p2 = self.first_intersections[i], self.first_intersections[i + 1]
            b1, b2 = self.second_intersections[i], self.second_intersections[i + 1]

            # Triangle 1: (p1, p2, b1)
            glVertex2f(p1[0], p1[1])
            glVertex2f(p2[0], p2[1])
            glVertex2f(b1[0], b1[1])

            # Triangle 2: (b1, p2, b2)
            glVertex2f(b1[0], b1[1])
            glVertex2f(p2[0], p2[1])
            glVertex2f(b2[0], b2[1])

        glEnd()



if __name__ == "__main__":
    myApp = App()
    myApp.mainLoop()
    myApp.quit()
