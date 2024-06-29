import bpy
from mathutils import Vector

class BlenderObject:
    def __init__(self, vertices, extrusion_direction, extrusion_length):
        self.vertices = [Vector(v) for v in vertices]
        self.extrusion_direction = extrusion_direction.lower()
        self.extrusion_length = extrusion_length
  
    # a method to shift the vertices of the object
    def shift(self, shift_vector):
        shift_vector = Vector(shift_vector)
        for vertex in self.vertices:
            vertex += shift_vector

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
BlenderObject(vertices, 'z', 1).build()
