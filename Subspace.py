# Create a 3d subspace

# randomize creating a cube with a rotation factor in 

#test launching a ray to see if a ray can intersect a cube

# find dot product of that cube

import numpy as np

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = np.array(v1)
        self.v2 = np.array(v2)
        self.v3 = np.array(v3)

class Shape:
    def __init__(self):
        self.triangles = []

    def add_triangle(self, triangle):
        self.triangles.append(triangle)

class Cube(Shape):

    def __init__(self, center=(0, 0, 0), size=1.0):

        """
        Represents a cube.
        
        :param center: Center of the cube (x, y, z)
        :param size: Size of the cube
        """
        super().__init__()
        self.center = np.array(center)
        self.size = size
        
        # Define vertices of the cube
        vertices = [
            self.center + np.array([-size/2, -size/2, -size/2]),
            self.center + np.array([size/2, -size/2, -size/2]),
            self.center + np.array([size/2, size/2, -size/2]),
            self.center + np.array([-size/2, size/2, -size/2]),
            self.center + np.array([-size/2, -size/2, size/2]),
            self.center + np.array([size/2, -size/2, size/2]),
            self.center + np.array([size/2, size/2, size/2]),
            self.center + np.array([-size/2, size/2, size/2]),
        ]
        
        # Define triangles of the cube
        triangles = [
            (vertices[0], vertices[1], vertices[2]),
            (vertices[2], vertices[3], vertices[0]),
            (vertices[4], vertices[5], vertices[6]),
            (vertices[6], vertices[7], vertices[4]),
            (vertices[0], vertices[4], vertices[5]),
            (vertices[5], vertices[1], vertices[0]),
            (vertices[1], vertices[5], vertices[6]),
            (vertices[6], vertices[2], vertices[1]),
            (vertices[2], vertices[6], vertices[7]),
            (vertices[7], vertices[3], vertices[2]),
            (vertices[3], vertices[7], vertices[4]),
            (vertices[4], vertices[0], vertices[3]),
        ]
        
        # Add triangles to the shape
        for v1, v2, v3 in triangles:
            self.add_triangle(Triangle(v1, v2, v3))
        
cube = Cube((1,2,2), 4)