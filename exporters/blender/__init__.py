# Despair Engine Model Exporter
import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
)
from bpy.types import Operator  # B2.8
from bpy_extras.io_utils import ExportHelper, ImportHelper

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

import logging

if "bpy" in locals():
    import importlib
    if "import_dem" in locals():
        importlib.reload(import_dem)
    if "export_dem" in locals():
        importlib.reload(export_dem)
    if "common_dem" in locals():
        importlib.reload(common_dem)
    if "datamodels" in locals():
        importlib.reload(datamodels)
else:
    import common_dem
    import dataclasses
    import import_dem
    import export_dem

from .datamodels import (
    Vert,
    Tri,
    Joint,
    AnimJoint,
    Clip,
    Frame,
    Weight
)

bl_info = {
    "name": "Despair Engine Models (dem, dema)",
    "description": "Importer and exporter for the DEM file format (dem, dema)",
    "author": "Kyle 'Ninja Ghost'",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "File > Import/Export > Despair Engine Models",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s',)

# The model format essentially apes off of a weird marriage between obj and md5
# in that the overall text file format is obj-like in style, purposely stupidly easy to parse 
# but the essential data flow follows md5's lead. Such as defining joints, weights and animation data
# There's some unique concessions of my own, like packing as much vertex data into one line as possible in the exact
# same format as I like to describe my vertex buffers, and only supporting triangles. 

def triangulateMesh_fn(object, depsgraph, tri=False):
    ''' only triangulate selected mesh '''
    if not object.type == 'MESH':
        return None, None
    
    print("Doing the triangulation thing")

    depMesh = object.evaluated_get(depsgraph)  # .original.to_mesh()
    print(f" = depMesh {str(depMesh)}")
    outMesh = depMesh.to_mesh()  # .original.to_mesh()
    print(f" = outMesh {str(outMesh)}")
    outMesh.transform(object.matrix_world)  # added 1.21
    print(f" = outMesh {str(outMesh)}")
    #  outMesh = object.data  # .original.to_mesh() # working old 2.8.0
    #  ###tmp_mesh.to_mesh_clear()disable if not used

    if outMesh is None or not object.type == 'MESH':
        print("to_mesh_clear()")
        depMesh.to_mesh_clear()
        return None, None

    if not outMesh.loop_triangles and outMesh.polygons:
        print("calc_loop_triangles()")
        outMesh.calc_loop_triangles()

    print("I guess we did the triangulation thing")

    return outMesh, depMesh

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()



def write_some_data(context, filepath, use_some_setting):
    print("running writer...")
    f = open(filepath, 'w', encoding='utf-8')

    depsgraph = bpy.context.evaluated_depsgraph_get()


    # # Apply a Triangulate Modifier to all mesh objects
    # for obj in bpy.context.scene.objects:
    #     if obj.type == 'MESH':
    #         mod = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
    #         # Configure the modifier if needed

    f.write("{}_{}\n".format("DEM", "10"))

    # scene = bpy.context.scene
    scene = depsgraph.object_instances

    """
    Phase 1: Header.
    """

    num_meshes = 0
    num_joints = 0
    for obj_instance in scene:
        obj = obj_instance.object 
        if obj.type == 'MESH':
            num_meshes+=1
        elif obj.type == 'JOINT':
            num_joints+=1

    f.write("joints {}\n".format(num_joints))
    # for obj in scene.objects:
    #     if obj.type == 'JOINT':
    #         print("Discovered joint")
    #         # j jointName parentIndex vx vy vz rx ry rz 

    f.write("meshes {}\n".format(num_meshes))


    """
    Phase 2: Models and Meshes
    """

    for obj_instance in scene:
        obj = obj_instance.object


        if obj.type == 'MESH':
            print("Discovered object %s" % obj.name)
            f.write("mesh %s\n" % obj.name)
    
            ### We only support triangles, so we force the issue 
            # tmp_mesh, depMesh = triangulateMesh_fn(obj, depsgraph)
            # tmp_mesh = mesh_triangulate(obj.original.to_mesh())
            # if tmp_mesh is None:
                # continue


            mesh = obj.data
            tmp_mesh = mesh 
            mesh_loops = tmp_mesh.loops
            uv_layer = tmp_mesh.uv_layers.active.data

            if not tmp_mesh.vertex_colors:
                tmp_mesh.vertex_colors.new()
                logging.debug("Mesh had no vertex colors, adding them")
                print(f"Mesh had no vertex colors, adding them")

            color_layer = tmp_mesh.vertex_colors.active.data    # this was tripping errors

            if bpy.context.mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='OBJECT')

            f.write("mat lightmapped_generic\n")

            # Gather Vertices
            f.write("verts {}\n".format(len(tmp_mesh.vertices)))
            vert_array = []
            for vertex in tmp_mesh.vertices:
                vert_array.append(Vert(
                    vertex.index,
                    vertex.co.x,
                    vertex.co.y,
                    vertex.co.z,
                    vertex.normal.x,
                    vertex.normal.y,
                    vertex.normal.z
                ))

            for poly in tmp_mesh.polygons:
                # print(f"  Face {poly.index}:")
                for li in poly.loop_indices:
                    loop = tmp_mesh.loops[li]
                    loop_idx = loop.vertex_index
                    uv = uv_layer[li].uv
                    color = color_layer[li].color
                    # print(f"    Loop {li}: Vertex {loop_idx} UV = {uv}")
                    vert_array[loop_idx].u = uv.x
                    vert_array[loop_idx].v = uv.y
                    vert_array[loop_idx].r = color[0]
                    vert_array[loop_idx].g = color[1]
                    vert_array[loop_idx].b = color[2]
                    # print(f"    Loop {li}: Vertex {loop_idx} UV = {uv}
                    # Color = (R: {color[0]}, G: {color[1]}, B: {color[2]})")

            for vertex in vert_array:
                # v idx vx vy vz nx ny nz tu tv cr cg cb
                f.write(str(vertex))

            # Gather Faces
            face_array = []
            for poly in tmp_mesh.polygons:
                print(f"  Face {str(poly)}:")

                t = Tri(
                    poly.index
                )
                triCounter = 0
                for li in poly.loop_indices:
                    print(f"    - li: {li}")
                    # if li <= 2:
                    loop = mesh.loops[li]
                    print(f"    - loop: {loop}")
                    loop_idx = loop.vertex_index
#                        setattr(t, f'v{li+1}', loop_idx)
                    if triCounter == 0:
                        t.v1 = loop_idx
                    elif triCounter == 1:
                        t.v2 = loop_idx
                    elif triCounter == 2:
                        t.v3 = loop_idx
                        face_array.append(t)
                        t = Tri(
                            poly.index
                        )

                    triCounter += 1
                    if triCounter > 2:
                        triCounter = 0


                

            f.write("tris {}\n".format(len(face_array)))
            for face in face_array:
                f.write(str(face))

            # Gather Weights
            weight_array = []
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
        name="Format",
        description="Export Mode",
        items=(
            ('DEM_ALL', "DEM (Packed)", "(Default) Everything in one .dem file"),
            ('DEM_DEMA', "DEM & DEMA", "Model and Animation files split"),
            ('DEM_ONLY', "DEM (Model)", "Just Model data, no animation"),
            ('DEMA_ONE', "DEMA (Single)", "Just Animation, no Model, don't split by Marker"),
            ('DEMA_MULT', "DEMA (Multiple)", "Just Animation, no Model, split by Marker"),
        ),
        default='DEM_ALL',
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
    # bpy.ops.export_test.some_data('INVOKE_DEFAULT')
