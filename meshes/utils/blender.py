import bpy


def add_mesh(name, verticies, edges=[], faces=[]):
    new_mesh = bpy.data.meshes.new(name)
    new_mesh.from_pydata(verticies, edges, faces)
    if new_mesh.validate():
        print('Invalid mesh')
        return
    new_mesh.update()
    new_object = bpy.data.objects.new(name, new_mesh)
    new_collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(new_collection)
    new_collection.objects.link(new_object)


def create_mesh(name, verts=[], edges=[], faces=[], validate=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    if validate:
        if mesh.validate():
            print('Invalid mesh')
            return
    return mesh


def attach_mesh(name, mesh):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def new_mesh_obj(mesh_name, verts, edges=[], faces=[], obj_name=None, validate=True):
    if not obj_name:
        obj_name = mesh_name
    mesh = create_mesh(mesh_name, verts, edges, faces, validate)
    obj = attach_mesh(obj_name, mesh)
    return obj


def join_meshes(objs: list):
    ctx = bpy.context.copy()
    ctx['active_object'] = objs[0]
    ctx['selected_editable_objects'] = objs
    result = bpy.ops.object.join(ctx)
    name = objs[0].name.rsplit('__face_0', 1)
    name = ''.join(name)
    objs[0].name = name
    return result
