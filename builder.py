import bpy
from mathutils import Vector

class BlenderObject:
    def __init__(self, vertices, extrusion_direction, extrusion_length):
        self.vertices = [Vector(v) for v in vertices]
        self.extrusion_direction = extrusion_direction.lower()
        self.extrusion_length = extrusion_length
  
    # a method to shift the vertices of the object
    def shift(self, shift_x, shift_y, shift_z):
        shift_vector = Vector([shift_x, shift_y, shift_z])
        for i in range(len(self.vertices)):
            self.vertices[i] += shift_vector

    def align(
        self,
        bottom_x=None, bottom_y=None, bottom_z=None,
        center_x=None, center_y=None, center_z=None,
        top_x=None, top_y=None, top_z=None
    ):
        # Calculate the center of the object
        center = Vector([0, 0, 0])
        for v in self.vertices:
            center += v
        center /= len(self.vertices)
        
        # Calculate the bottom of the object
        bottom = Vector([0, 0, 0])
        for v in self.vertices:
            bottom = Vector([min(bottom[i], v[i]) for i in range(3)])
        
        # Calculate the top of the object
        top = Vector([0, 0, 0])
        for v in self.vertices:
            top = Vector([max(top[i], v[i]) for i in range(3)])
        
        # Calculate the shift vector
        shift_vector = Vector([0, 0, 0])
        if bottom_x is not None:
            shift_vector[0] = bottom_x - bottom[0]
        if bottom_y is not None:
            shift_vector[1] = bottom_y - bottom[1]
        if bottom_z is not None:
            shift_vector[2] = bottom_z - bottom[2]
        if center_x is not None:
            shift_vector[0] = center_x - center[0]
        if center_y is not None:
            shift_vector[1] = center_y - center[1]
        if center_z is not None:
            shift_vector[2] = center_z - center[2]
        if top_x is not None:
            shift_vector[0] = top_x - top[0]
        if top_y is not None:
            shift_vector[1] = top_y - top[1]
        if top_z is not None:
            shift_vector[2] = top_z - top[2]
        
        # Shift the vertices
        for i in range(len(self.vertices)):
            self.vertices[i] += shift_vector
    
    def bottom_x(self):
        return min([v[0] for v in self.vertices])
    def bottom_y(self):
        return min([v[1] for v in self.vertices])
    def bottom_z(self):
        return min([v[2] for v in self.vertices])
    def center_x(self):
        return sum([v[0] for v in self.vertices]) / len(self.vertices)
    def center_y(self):
        return sum([v[1] for v in self.vertices]) / len(self.vertices)
    def center_z(self):
        return sum([v[2] for v in self.vertices]) / len(self.vertices)
    def top_x(self):
        return max([v[0] for v in self.vertices])
    def top_y(self):
        return max([v[1] for v in self.vertices])
    def top_z(self):
        return max([v[2] for v in self.vertices])

    # a method to build the object
    def build(self):
        # create a new mesh
        mesh = bpy.data.meshes.new('mesh')
        mesh.from_pydata(self.vertices, [], [(0, 1, 2, 3)])  # Define faces
        mesh.update()
        
        # create an object from the mesh
        obj = bpy.data.objects.new('object', mesh)
        bpy.context.collection.objects.link(obj)
        
        # select the object and set it as active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # extrude the object in either x, y, or z direction
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (
                (self.extrusion_length, 0, 0) if self.extrusion_direction == 'x' else
                (0, self.extrusion_length, 0) if self.extrusion_direction == 'y' else
                (0, 0, self.extrusion_length) if self.extrusion_direction == 'z' else
                (0, 0, 0)
            )}
        )
        bpy.ops.object.mode_set(mode='OBJECT')

# Delete all objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# create a test cube
vertices = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
test_cube_1 = BlenderObject(vertices, 'z', 1)
test_cube_1.shift(-0.5,-0.5,-0.5)
test_cube_1.align(bottom_x=0, bottom_y=0)
test_cube_2 = BlenderObject(vertices, 'z', 1)
test_cube_2.align(center_x=test_cube_1.center_x(), center_y=test_cube_1.center_y(), bottom_z=test_cube_1.top_z())
test_cube_1.build()
test_cube_2.build()
