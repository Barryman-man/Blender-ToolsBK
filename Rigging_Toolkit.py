import bpy

#########################################################################
# Barry Rigging toolkit. - Blender 5.x and above - rigify API Changes   #
# Current tools                                                         #
# - Prop Colors/Groups                                                  #
#   - Adds custom colors sets, creates required bone groups and         #
#       connects for props.                                             #
# - Character Colors/Groups                                             #
#   - Adds custom colors sets, creates required bone groups and         #
#       connects for Characters.                                        #
# - Hard Weight to Bone                                                 #
#    - takes bone name coppied to clipboard                             #
#    - creates vertex group with that name                              #
#    - assignes all verticies from object to that vertex group          #
#                                                                       #
#   - TODO: - Better check for existing colors and groups               #
#           - or Remove exisitng colors and groups before adding        #
#           - thurough commenting                                       #
#           - add armature modifier to object                           #
#########################################################################


class RIG_OT_add_bone_props_collections_and_colors(bpy.types.Operator):
    """Adds Custom Color Set, Bone Groups and connects for props"""
    bl_idname = "rigging.add_custom_props_groups_and_colors"
    bl_label = "Add Custom Colors, groups and connects them"
    
    def execute(self, context):
        def check_rigify_colors(obj):
            if not obj or obj.type != 'ARMATURE':
                return False

            colors = getattr(obj.data, "rigify_colors", None)

            if colors is not None and len(colors) == 8:
                return True

            return False

        if check_rigify_colors(bpy.context.object):
            print("Colors are ready to use!")
            
        else:
            print("Creating colors")
            bpy.ops.armature.rigify_color_set_remove_all()
            armature = bpy.ops.armature
            props = ("Root", "Root.001", "COG.001", "COG.002", "OBJ.001", "OBJ.002", "OBJ1.001", "OBJ1.002")
            colors = (0.435294, 0.184314, 0.415686, 0.156211, 0.131012, 0.305411, 0.956863, 0.788236, 0.0470588, 0.467974, 0.296512, 0.0230151, 0.117647, 0.568627, 0.0352941, 0.165505, 0.272679,0.0304802, 1, 0.00268805, 0, 1, 0.263096, 0.261111)
            
            colorIndex = 0
            colorSetIndex = 0
            
            for index, prop in enumerate(props):
                pairedColors = colors[colorIndex:colorIndex + 3]
                colorSet = colorSetIndex
                armature.rigify_color_set_add()
                bpy.context.object.data.rigify_colors[index].name = ''.join(prop)
                bpy.context.object.data.rigify_colors[index].normal = pairedColors
                colorIndex += 3
                colorSet += 1     

        def check_rigify_groups(obj):
            if not obj or obj.type != 'ARMATURE':
                return False

            groups = getattr(obj.data, "collections", None)

            if groups is not None and len(groups) == 8:
                return True

            return False

        if check_rigify_groups(bpy.context.object):
            print("Groups are ready to use!")
            
        else:
            print("Creating groups")
            # todo - remove old bone groups
            armature = bpy.ops.armature
            props = ("Root", "Root.001", "COG.001", "COG.002", "OBJ.001", "OBJ.002", "OBJ1.001", "OBJ1.002")
            
            for index, prop in enumerate(props):
                armature.collection_add()
                bpy.context.object.data.collections_all["Bones"].name = prop
            

        groupName = list(bpy.context.object.data.collections_all)
        colorName = ("Root", "Root.001", "COG.001", "COG.002", "OBJ.001", "OBJ.002", "OBJ1.001", "OBJ1.002")

        for group in groupName:
            for color in colorName:
                if color == group.name:
                    group.rigify_color_set_name = color

        return {"FINISHED"}


class RIG_OT_add_bone_character_collections_and_colors(bpy.types.Operator):
    """Adds Custom Character Bone Groups, colors and connectto Armature"""
    bl_idname = "rigging.add_custom_character_groups_and_colors"
    bl_label = "Add Custom Groups"
    
    def execute(self, context):
        def check_rigify_groups(obj):
            if not obj or obj.type != 'ARMATURE':
                return False

            groups = getattr(obj.data, "collections", None)

            if groups is not None and len(groups) == 24:
                return True

            return False

        if check_rigify_groups(bpy.context.object):
            print("Groups are ready to use!")
            
        else:
            print("Creating groups")
            # remove old bones
            armature = bpy.ops.armature
            props = ("Root", "Root.001", "Core", "Core Sub", "Finger.L", "Finger.L (Detail)", "Arm.L (FK)", "Arm.L (IK)", "Arm.L (Tweak)", "Leg.L", "Toes.L", "Leg.L (IK)", "Leg.L (FK)", "BodyAll", "FaceAll", "Finger.R", "Finger.R (Detail)", "Arm.R (FK)", "Arm.R (IK)", "Arm.R (Tweak)", "Leg.R", "Toes.R", "Leg.R (IK)", "Leg.R (FK)")
            
            for index, prop in enumerate(props):
                armature.collection_add()
                bpy.context.object.data.collections_all["Bones"].name = prop
        groupName = list(bpy.context.object.data.collections_all)

        def check_rigify_colors(obj):
            if not obj or obj.type != 'ARMATURE':
                return False

            colors = getattr(obj.data, "rigify_colors", None)

            if colors is not None and len(colors) == 8:
                return True

            return False

        if check_rigify_colors(bpy.context.object):
            print("Colors are ready to use!")
            
        else:
            print("Creating colors")
            bpy.ops.armature.rigify_color_set_remove_all()
            armature = bpy.ops.armature
            props = ("Root", "Root.001", "Right", "Right Sub", "Left", "Left Sub", "Core", "Core Sub")
            colors = (0.435294, 0.184314, 0.415686, 0.156211, 0.131012, 0.305411, 0.604, 0.000, 0.000, 0.736, 0.192, 0.201, 0.000, 0.004, 0.604, 0.005, 0.335, 0.604, 0.957, 0.788, 0.047, 0.468, 0.297, 0.023)

            colorIndex = 0
            colorSetIndex = 0
            
            for index, prop in enumerate(props):
                pairedColors = colors[colorIndex:colorIndex + 3]
                colorSet = colorSetIndex
                armature.rigify_color_set_add()
                bpy.context.object.data.rigify_colors[index].name = ''.join(prop)
                bpy.context.object.data.rigify_colors[index].normal = pairedColors
                colorIndex += 3
                colorSet += 1


        # left and sub left coloring
            groupName = list(bpy.context.object.data.collections_all)
            subGroups = ("(Detail)", "(Tweak)", "(Sub)")
            colorName = ("Root", "Root.001", "Core", "Core Sub")

            for group in groupName:
                if ".L" in group.name:
                    group.rigify_color_set_name = "Left"
                    for sub in subGroups:
                        if sub in group.name:
                            group.rigify_color_set_name = "LeftSub"
                if ".R" in group.name:
                    group.rigify_color_set_name = "Right"
                    for sub in subGroups:
                        if sub in group.name:
                            group.rigify_color_set_name = "RightSub"
                else:
                    for color in colorName:
                        if group.name == color:
                            group.rigify_color_set_name = color
        return {'FINISHED'}
    
    
class RIG_OT_hard_weight_to_coppied_bone(bpy.types.Operator):
    """Uses bone name coppied from clipboard to create a vertex group and assigning all vertices of object to the vertex group to help with hard weighting to a bone."""
    bl_idname = "rigging.hard_weight_to_coppied_bone"
    bl_label = "Creates a vertex group and assigns all vertices of object to it."
    
    def execute(self, context):
        # check if vertex group already exists
        vertexGroups = bpy.context.object.vertex_groups
        coppiedBone = bpy.context.window_manager.clipboard


        if coppiedBone in vertexGroups:
            print("vertex group already exists")

        else:
            newGroup = bpy.context.object.vertex_groups.new()
            newGroup.name = coppiedBone
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode='OBJECT')
            for armature in bpy.data.armatures:
                object = bpy.data.armatures[armature.name]
                if object.rigify_target_rig != None:
                    selectedObj = bpy.context.object
                    #if armature modifier already exists, pass
                    if not selectedObj.modifiers:
                        print("no mods")
                        armatureCNST = bpy.data.objects[selectedObj.name].modifiers.new(name='Armature', type='ARMATURE')
                        armatureCNST.object = object.rigify_target_rig                
                    else:
                        print("has mods")
            
        return {'FINISHED'}


   
# start of panel
class VIEW3D_PT_rigging_panel(bpy.types.Panel):
    
    # where to add panel in UI
    bl_space_type = "VIEW_3D" # which editor type will it be visible
    bl_region_type = "UI" # defines side bar (n-panel)
    
    # add label
    bl_category = "Rigging" # name of panel
    bl_label = "Rigging Panel" # name at the top of the panel
    
    def draw(self, context):
        """define the layout of the panel"""
        # begin panel generation

        row = self.layout.row() # define rows in draw
        row.operator("rigging.add_custom_props_groups_and_colors", text = "Prop Colors/Groups")
        row = self.layout.row()
        row.operator("rigging.add_custom_character_groups_and_colors", text = "Character Colors/Groups")
        row = self.layout.row()
        row.operator("rigging.hard_weight_to_coppied_bone", text = "Hard Weight to Bone")
        


# register the panel with Blender
def register():
    bpy.utils.register_class(RIG_OT_add_bone_props_collections_and_colors)
    bpy.utils.register_class(RIG_OT_add_bone_character_collections_and_colors)
    bpy.utils.register_class(RIG_OT_hard_weight_to_coppied_bone)
    bpy.utils.register_class(VIEW3D_PT_rigging_panel)

    
def unregister():
    bpy.utils.register_class(RIG_OT_add_bone_props_collections_and_colors)
    bpy.utils.unregister_class(VIEW3D_PT_rigging_panel)
    bpy.utils.register_class(RIG_OT_add_bone_character_collections_and_colors)
    bpy.utils.register_class(RIG_OT_hard_weight_to_coppied_bone)
        
if __name__ == "__main__":
    register()