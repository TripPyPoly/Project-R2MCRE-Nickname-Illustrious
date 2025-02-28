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
        self.intersections = []  # Store intersection points
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
            self.intersections.append((closest_intersection.x, closest_intersection.y))
            self.intersections.append((right_intersection.x, right_intersection.y))

            # Create triangle from:
            # 1. Intersection with square
            # 2. Intersection with right screen
            # 3. The ray's original left-side position
            self.triangles.append([
                (closest_intersection.x, closest_intersection.y),
                (right_intersection.x, right_intersection.y),
                (ray.coords[0][0], ray.coords[0][1])
            ])

    def draw_rays(self):
        """Draw only the latest ray and render gray continuation past the square."""
        if not self.rays:
            return

        latest_ray = self.rays[-1]  # Get the most recent ray

        # Draw the latest ray in green
        glColor3f(0, 1, 0)  # Green for main ray
        glBegin(GL_LINES)
        glVertex2f(latest_ray.coords[0][0], latest_ray.coords[0][1])
        glVertex2f(latest_ray.coords[1][0], latest_ray.coords[1][1])
        glEnd()

        # Draw the gray "continued" ray from the intersection to the right edge
        if len(self.intersections) >= 2:
            glColor3f(0.5, 0.5, 0.5)  # Gray for post-intersection rays
            glBegin(GL_LINES)
            for i in range(0, len(self.intersections), 2):
                start = self.intersections[i]    # Intersection with square
                end = self.intersections[i + 1]  # Intersection with right screen edge
                glVertex2f(start[0], start[1])
                glVertex2f(end[0], end[1])
            glEnd()

        # Draw "shadow" effect by making lines more opaque behind the square
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_LINES)
        for i, (start, end) in enumerate(zip(self.intersections[::2], self.intersections[1::2])):
            opacity = min(1.0, (i + 1) / len(self.intersections))  # Increase opacity over time
            glColor4f(0.2, 0.2, 0.2, opacity)  # Dark gray with increasing opacity
            glVertex2f(start[0], start[1])
            glVertex2f(end[0], end[1])
        glEnd()
        glDisable(GL_BLEND)



    def draw_triangles(self):
        """Draw the generated triangles."""
        glColor3f(0, 0, 1)  # Blue triangles
        glBegin(GL_TRIANGLES)
        for tri in self.triangles:
            for x, y in tri:
                glVertex2f(x, y)
        glEnd()


if __name__ == "__main__":
    myApp = App()
    myApp.mainLoop()
    myApp.quit()
