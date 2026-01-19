import bpy

# ======================================================
# OPERATOR
# ======================================================

class OBJECT_OT_match_transforms(bpy.types.Operator):
    bl_idname = "object.match_transforms"
    bl_label = "Match Transforms"
    bl_description = "Copy transforms from Collection A to Collection B (by index)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        col_a = scene.match_collection_a
        col_b = scene.match_collection_b

        if not col_a or not col_b:
            self.report({'ERROR'}, "Please select both collections")
            return {'CANCELLED'}

        objects_a = list(col_a.objects)
        objects_b = list(col_b.objects)

        if not objects_a or not objects_b:
            self.report({'ERROR'}, "One or both collections are empty")
            return {'CANCELLED'}

        # Use smallest length
        array_length = min(len(objects_a), len(objects_b))

        for i in range(array_length):
            obj_b = objects_b[i]
            obj_a = objects_a[i]
            
            # Copy world transform
            obj_b.matrix_world = obj_a.matrix_world.copy()

        self.report({'INFO'}, f"Matched {array_length} transforms")
        return {'FINISHED'}


# ======================================================
# UI PANEL
# ======================================================

class VIEW3D_PT_match_transforms(bpy.types.Panel):
    bl_label = "Match Transforms"
    bl_idname = "VIEW3D_PT_match_transforms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PEEKMacros"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Source (A):")
        layout.prop(scene, "match_collection_a", text="")
        
        layout.label(text="Target (B):")
        layout.prop(scene, "match_collection_b", text="")
        
        layout.separator()
        layout.operator("object.match_transforms", icon='CON_TRANSLIKE')


# ======================================================
# REGISTRATION
# ======================================================

classes = (
    OBJECT_OT_match_transforms,
    VIEW3D_PT_match_transforms,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.match_collection_a = bpy.props.PointerProperty(
        name="Collection A",
        type=bpy.types.Collection,
        description="Source collection (transforms will be copied FROM here)"
    )
    
    bpy.types.Scene.match_collection_b = bpy.props.PointerProperty(
        name="Collection B",
        type=bpy.types.Collection,
        description="Target collection (transforms will be copied TO here)"
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.match_collection_a
    del bpy.types.Scene.match_collection_b

if __name__ == "__main__":
    register()