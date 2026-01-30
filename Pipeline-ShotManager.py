bl_info = {
    "name": "Shot Manager",
    "author": "Barry Karnowski",
    "version": (1, 3, 1),
    "blender": (4, 4, 0),
    "location": "View3D > UI > Two Pints",
    "description": "Manage Episodes, Sequences, and Shots.",
    "category": "Pipeline",
}

import bpy
import os
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, EnumProperty, PointerProperty

# Helper functions
def list_dir_enum(path):
    if os.path.isdir(path):
        return [(d, d, "") for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return [("NONE", "None Found", "")]

def get_next_increment_filename(folder, base_name):
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
        return f"{base_name}_v001.blend"

    existing = [f for f in os.listdir(folder) if f.startswith(base_name) and f.endswith(".blend")]
    numbers = []

    for f in existing:
        name_without_ext = f[:-6] if f.endswith(".blend") else f
        if "_v" in name_without_ext:
            parts = name_without_ext.rsplit("_v", 1)
            if len(parts) == 2 and parts[1].isdigit():
                numbers.append(int(parts[1]))

    next_number = max(numbers, default=0) + 1
    return f"{base_name}_v{str(next_number).zfill(3)}.blend"

def get_latest_version(directory, base_name):
    if not os.path.isdir(directory):
        return None
    latest_file = None
    latest_num = -1
    for f in os.listdir(directory):
        if f.startswith(base_name) and f.endswith(".blend"):
            name_without_ext = f[:-6] if f.endswith(".blend") else f
            if "_v" in name_without_ext:
                parts = name_without_ext.rsplit("_v", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    v = int(parts[1])
                    if v > latest_num:
                        latest_num = v
                        latest_file = f
    return os.path.join(directory, latest_file) if latest_file else None

# Property Group
class ShotSelectorProperties(PropertyGroup):
    series_directory: StringProperty(
        name="Series Directory",
        subtype='DIR_PATH',
        default="Z:\\",
        update=lambda self, context: self.update_episode_enum()
    )

    episode_enum: EnumProperty(
        name="Episode",
        description="Auto-discovered Episodes",
        items=lambda self, context: list_dir_enum(os.path.join(bpy.path.abspath(self.series_directory), "wip", "Shots")), # Changed
        update=lambda self, context: self.sync_episode_name()
    )
    episode_name: StringProperty(name="Episode Name", default="")

    sequence_enum: EnumProperty(
        name="Sequence",
        description="Auto-discovered Sequences",
        items=lambda self, context: list_dir_enum(os.path.join(bpy.path.abspath(self.series_directory), "wip", "Shots", self.episode_name or self.episode_enum)), # Changed
        update=lambda self, context: self.sync_sequence_name()
    )
    sequence_name: StringProperty(name="Sequence Name", default="")

    shot_enum: EnumProperty(
        name="Shot",
        description="Auto-discovered Shots",
        items=lambda self, context: list_dir_enum(os.path.join(bpy.path.abspath(self.series_directory), "wip", "Shots", self.episode_name or self.episode_enum, self.sequence_name or self.sequence_enum)), # Changed
        update=lambda self, context: self.sync_shot_name()
    )
    shot_name: StringProperty(name="Shot Name", default="")

    def sync_episode_name(self):
        self.episode_name = self.episode_enum

    def sync_sequence_name(self):
        self.sequence_name = self.sequence_enum

    def sync_shot_name(self):
        self.shot_name = self.shot_enum

    def get_shot_path(self, subfolder):
        # The 'subfolder' argument will be "wip" or "publish".
        # We need to insert "Shots" only for the "wip" path.
        if subfolder == "wip":
            return os.path.join(
                bpy.path.abspath(self.series_directory),
                subfolder,
                "Shots", # Added "Shots"
                self.episode_name,
                self.sequence_name,
                self.shot_name
            )
        else: # For "publish" or any other subfolder, keep the original structure
            return os.path.join(
                bpy.path.abspath(self.series_directory),
                subfolder,
                self.episode_name,
                self.sequence_name,
                self.shot_name
            )


# Save Logic
class SaveShotFile:
    def __init__(self, props: ShotSelectorProperties):
        self.props = props

    def save(self, mode="wip", incremental=True):
        path = self.props.get_shot_path(mode)
        os.makedirs(path, exist_ok=True)
        base = f"{self.props.episode_name}_{self.props.sequence_name}_{self.props.shot_name}"
        filename = get_next_increment_filename(path, base) if incremental else f"{base}.blend"
        save_path = os.path.join(path, filename)
        bpy.ops.wm.save_as_mainfile(filepath=save_path, copy=False)
        print(f"Saved to {save_path}")
        return save_path

# Operators
class SaveWIP(Operator):
    bl_idname = "shot.save_wip"
    bl_label = "Save WIP"

    def execute(self, context):
        props = context.scene.shot_selector_props
        if not all([props.series_directory, props.episode_name, props.sequence_name, props.shot_name]):
            self.report({'ERROR'}, "All fields must be filled!")
            return {'CANCELLED'}
        logic = SaveShotFile(props)
        try:
            path = logic.save("wip", incremental=True)
            self.report({'INFO'}, f"Saved: {path}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Save failed: {e}")
            return {'CANCELLED'}

class PublishShot(Operator):
    bl_idname = "shot.publish"
    bl_label = "Publish Shot"

    def execute(self, context):
        props = context.scene.shot_selector_props
        if not all([props.series_directory, props.episode_name, props.sequence_name, props.shot_name]):
            self.report({'ERROR'}, "All fields must be filled!")
            return {'CANCELLED'}
        logic = SaveShotFile(props)
        try:
            path = logic.save("publish", incremental=True)
            self.report({'INFO'}, f"Published: {path}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Publish failed: {e}")
            return {'CANCELLED'}

class LoadLatestWIP(Operator):
    bl_idname = "shot.load_latest_wip"
    bl_label = "Load Latest WIP"

    def execute(self, context):
        props = context.scene.shot_selector_props
        path = props.get_shot_path("wip")
        base = f"{props.episode_name}_{props.sequence_name}_{props.shot_name}"
        file = get_latest_version(path, base)
        if file:
            bpy.ops.wm.open_mainfile(filepath=file)
            self.report({'INFO'}, f"Loaded: {file}")
            return {'FINISHED'}
        self.report({'ERROR'}, "No WIP found")
        return {'CANCELLED'}

class LoadLatestPublish(Operator):
    bl_idname = "shot.load_latest_publish"
    bl_label = "Load Latest Publish"

    def execute(self, context):
        props = context.scene.shot_selector_props
        path = props.get_shot_path("publish")
        base = f"{props.episode_name}_{props.sequence_name}_{props.shot_name}"
        file = get_latest_version(path, base)
        if file:
            bpy.ops.wm.open_mainfile(filepath=file)
            self.report({'INFO'}, f"Loaded: {file}")
            return {'FINISHED'}
        self.report({'ERROR'}, "No publish found")
        return {'CANCELLED'}

# UI Panel
class ShotManagerPanel(Panel):
    bl_label = "Shot Manager"
    bl_idname = "VIEW3D_PT_shot_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Two Pints'

    def draw(self, context):
        layout = self.layout
        props = context.scene.shot_selector_props

        layout.prop(props, "series_directory")
        layout.separator()

        col = layout.box().column()
        col.label(text="Episode:")
        row = col.row(align=True)
        row.prop(props, "episode_enum", text="")
        row.prop(props, "episode_name", text="")

        col = layout.box().column()
        col.label(text="Sequence:")
        row = col.row(align=True)
        row.prop(props, "sequence_enum", text="")
        row.prop(props, "sequence_name", text="")

        col = layout.box().column()
        col.label(text="Shot:")
        row = col.row(align=True)
        row.prop(props, "shot_enum", text="")
        row.prop(props, "shot_name", text="")

        layout.separator()
        col = layout.column(align=True)
        col.operator("shot.load_latest_wip", text="Shot Load WIP", icon='VIEW_CAMERA_UNSELECTED')
        col.operator("shot.save_wip", text="Shot Save WIP", icon='CON_CAMERASOLVER')
        layout.separator()


# Registration
classes = [
    ShotSelectorProperties,
    SaveWIP,
    PublishShot,
    LoadLatestWIP,
    LoadLatestPublish,
    ShotManagerPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.shot_selector_props = PointerProperty(type=ShotSelectorProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.shot_selector_props

if __name__ == "__main__":
    register()
