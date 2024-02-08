# Despair Engine Model Exporter
import bpy
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)

# The model format essentially apes off of a weird marriage between obj and md5
# in that the overall text file format is obj-like in style, purposely stupidly easy to parse 
# but the essential data flow follows md5's lead. Such as defining joints, weights and animation data
# There's some unique concessions of my own, like packing as much vertex data into one line as possible in the exact
# same format as I like to describe my vertex buffers, and only supporting triangles. 

MAX_FLOAT_PRECISION = 16

@dataclass
class Vert:
    i: int      = 0
    vx: float   = 0.0
    vy: float   = 0.0
    vz: float   = 0.0
    nx: float   = 0.0
    ny: float   = 0.0
    nz: float   = 0.0
    u: float    = 0.0
    v: float    = 0.0
    r: float    = 0.0
    g: float    = 0.0
    b: float    = 0.0
    
    def __str__(self):
        return "v {} {} {} {} {} {} {} {} {} {} {} {}\n".format(
            self.i, 
            round(self.vx, MAX_FLOAT_PRECISION),
            round(self.vy, MAX_FLOAT_PRECISION),
            round(self.vz, MAX_FLOAT_PRECISION),
            round(self.nx, MAX_FLOAT_PRECISION),
            round(self.ny, MAX_FLOAT_PRECISION),
            round(self.nz, MAX_FLOAT_PRECISION),
            round(self.u, MAX_FLOAT_PRECISION),
            round(self.v, MAX_FLOAT_PRECISION),
            round(self.r, MAX_FLOAT_PRECISION),
            round(self.g, MAX_FLOAT_PRECISION),
            round(self.b, MAX_FLOAT_PRECISION)
        )
    
@dataclass
class Joint:
    name: str
    parent: int = -1
    vx: float   = 0.0
    vy: float   = 0.0
    vz: float   = 0.0 
    rx: float   = 0.0
    ry: float   = 0.0
    rz: float   = 0.0

    def __str__(self):
        return "j {} {} {} {} {} {} {} {}\n".format(
            self.name,
            self.parent,
            round(self.vx, MAX_FLOAT_PRECISION),
            round(self.vy, MAX_FLOAT_PRECISION),
            round(self.vz, MAX_FLOAT_PRECISION),
            round(self.rx, MAX_FLOAT_PRECISION),
            round(self.ry, MAX_FLOAT_PRECISION),
            round(self.rz, MAX_FLOAT_PRECISION) 
        )

@dataclass 
class Tri:
    i: int
    v1: int = 0
    v2: int = 0
    v3: int = 0

    def __str__(self):
        return "t {} {} {} {}\n".format(
            self.i,
            self.v1,
            self.v2,
            self.v3 
        )
    
@dataclass 
class Weight:
    i: int 
    j: int 
    w: float 
    x: float 
    y: float 
    z: float 

    def __str__(self):
        return "w {} {} {} {} {} {}\n".format(
            self.i,
            self.j,
            round(self.w, MAX_FLOAT_PRECISION),
            round(self.x, MAX_FLOAT_PRECISION),
            round(self.y, MAX_FLOAT_PRECISION),
            round(self.z, MAX_FLOAT_PRECISION) 
        )



#### ANIM FORMAT
@dataclass 
class AnimJoint:
    joint: Joint   # to reference name and parent index 
    flags: int 
    start_index: int  # not sure if I need this for my purposes

    def __str__(self):
        return "h "

@dataclass
class Frame:
    i: int 
    tx: float 
    ty: float 
    tz: float 
    rx: float 
    ry: float 
    rz: float 

    def __str__(self):
        return "f "
    
@dataclass
class Clip:
    joints: [Joint]
    frameRate: int 





def write_some_data(context, filepath, use_some_setting):
    print("running writer...")
    f = open(filepath, 'w', encoding='utf-8')
    
    
    # Apply a Triangulate Modifier to all mesh objects
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mod = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
            # Configure the modifier if needed
    

    f.write("DEM_10\n")
    
    scene = bpy.context.scene 
    
    numMeshes = 0
    numJoints = 0
    for obj in scene.objects: 
        if obj.type == 'MESH':
            numMeshes+=1
        elif obj.type == 'JOINT':
            numJoints+=1
    
    
    f.write("joints {}\n".format(numJoints))
    for obj in scene.objects:
        if obj.type == 'JOINT':
            print("Discovered joint")
            # j jointName parentIndex vx vy vz rx ry rz 
    
    
    f.write("meshes {}\n".format(numMeshes))
    for obj in scene.objects:
        if obj.type == 'MESH':
            print("Discovered object %s" % obj.name)
            f.write("mesh %s\n" % obj.name)

            mesh = obj.data 
            uv_layer = mesh.uv_layers.active.data
            
            if not mesh.vertex_colors:
                mesh.vertex_colors.new()
                #logging.debug("Mesh had no vertex colors, adding them")
                print(f"Mesh had no vertex colors, adding them")
            
            color_layer = mesh.vertex_colors.active.data    # this was tripping errors
            
            if bpy.context.mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='OBJECT')
                
            f.write("mat lightmapped_generic\n")
            
            ### Gather Vertices
            f.write("verts {}\n".format(len(mesh.vertices)))
            VertArray = []
            for vertex in mesh.vertices:
                VertArray.append(Vert(
                    vertex.index, 
                    vertex.co.x, 
                    vertex.co.y, 
                    vertex.co.z, 
                    vertex.normal.x, 
                    vertex.normal.y, 
                    vertex.normal.z
                ))
            
            
            for poly in mesh.polygons:
                #print(f"  Face {poly.index}:")
                for li in poly.loop_indices:
                    loop = mesh.loops[li]
                    loop_idx = loop.vertex_index
                    uv = uv_layer[li].uv
                    color = color_layer[li].color
#                    print(f"    Loop {li}: Vertex {loop_idx} UV = {uv}")
                    VertArray[loop_idx].u = uv.x
                    VertArray[loop_idx].v = uv.y
                    VertArray[loop_idx].r = color[0]
                    VertArray[loop_idx].g = color[1]
                    VertArray[loop_idx].b = color[2]
                    #print(f"    Loop {li}: Vertex {loop_idx} UV = {uv} Color = (R: {color[0]}, G: {color[1]}, B: {color[2]})")

            for vertex in VertArray:
                # v idx vx vy vz nx ny nz tu tv cr cg cb
                f.write(str(vertex))
                
                
            ### Gather Faces
            FaceArray = []
            for poly in mesh.polygons:
                print(f"  Face {poly.index}:")
                
                t = Tri(
                    poly.index
                )
                for li in poly.loop_indices:
                    if li <= 2:
                        loop = mesh.loops[li]
                        loop_idx = loop.vertex_index
#                        setattr(t, f'v{li+1}', loop_idx)
                        if li == 0:
                            t.v1 = loop_idx
                        elif li == 1:
                            t.v2 = loop_idx
                        elif li == 2:
                            t.v3 = loop_idx
                FaceArray.append(t)
                    
            f.write("tris {}\n".format(len(FaceArray)))
            # t idx vidx vidx vidx
            for face in FaceArray:
                f.write(str(face))
                    
            
            ### Gather Weights
            WeightArray = []
            f.write("weights {}\n".format(0))
            # w idx jidx weight x y z
    
    
#    f.write("Hello World %s" % use_some_setting)
    f.close()
    
    # Remove the Triangulate Modifier after export
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for mod in obj.modifiers:
                if mod.type == 'TRIANGULATE':
                    obj.modifiers.remove(mod)

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Some Data"

    # ExportHelper mixin class uses this
    filename_ext = ".dem"

    filter_glob: StringProperty(
        default="*.dem",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="Despair Engine Model (.dem)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
