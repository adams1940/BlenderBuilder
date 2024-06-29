import bpy
from mathutils import Vector

class BlenderObject:
    def __init__(self, vertices, extrusion_direction, extrusion_length):
        self.vertices = [Vector(v) for v in vertices]
        self.extrusion_direction = extrusion_direction.lower()
        self.extrusion_length = extrusion_length
        self.obj = None  # Initialize obj as None

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
        self.obj = bpy.data.objects.new('object', mesh)
        bpy.context.collection.objects.link(self.obj)
        
        # select the object and set it as active
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        
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

    # a method to remove another object from this object using a boolean operation
    def remove(self, other):
        # Ensure both objects exist
        if self.obj is None or other.obj is None:
            raise ValueError("Both objects must be built before performing boolean operations.")

        # Select both objects
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        other.obj.select_set(True)

        # Add and apply boolean modifier
        boolean_modifier = self.obj.modifiers.new(name="Boolean", type='BOOLEAN')
        boolean_modifier.operation = 'DIFFERENCE'
        boolean_modifier.object = other.obj
        bpy.ops.object.modifier_apply(modifier=boolean_modifier.name)
        
        # Deselect the other object
        other.obj.select_set(False)

        # Delete the other object
        bpy.data.objects.remove(other.obj, do_unlink=True)
        other.obj = None  # Ensure the reference to the deleted object is cleared

class Block(BlenderObject):
    def __init__(self, length, width, height):
        # Define the 8 vertices of the block (a rectangular prism)
        vertices = [
            (0, 0, 0),
            (length, 0, 0),
            (length, width, 0),
            (0, width, 0),
            (0, 0, height),
            (length, 0, height),
            (length, width, height),
            (0, width, height)
        ]
        # We do not need to extrude since we already define the height
        super().__init__(vertices, '', 0)

    def build(self):
        # create a new mesh
        mesh = bpy.data.meshes.new('BlockMesh')
        # Define faces for the rectangular prism
        faces = [
            (0, 1, 2, 3),  # bottom face
            (4, 5, 6, 7),  # top face
            (0, 1, 5, 4),  # side face 1
            (1, 2, 6, 5),  # side face 2
            (2, 3, 7, 6),  # side face 3
            (3, 0, 4, 7)   # side face 4
        ]
        mesh.from_pydata(self.vertices, [], faces)
        mesh.update()
        
        # create an object from the mesh
        self.obj = bpy.data.objects.new('Block', mesh)
        bpy.context.collection.objects.link(self.obj)
        
        # select the object and set it as active
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)

# Delete all objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Example usage:
# Create a block with length=2, width=1, height=3
block1 = Block(1,1,1)
block1.align(center_x=0, center_y=0, center_z=0)
block1.build()

block2 = Block(1,1,1)
block2.build()

# Remove block2 from block1
block1.remove(block2)
