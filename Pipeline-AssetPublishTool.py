bl_info = {
    "name": "Asset Manager",
    "author": "Barry Karnowski",
    "version": (1, 0, 0),
    "blender": (4, 4, 0),
    "location": "View3D > UI > Two Pints",
    "description": "Basic asset management for saving and loading Blender asset files.",
    "category": "Pipeline",
}

import bpy
import os
# from pathlib import Path # Not used
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, EnumProperty, PointerProperty

# ----------- Settings ------------
TASK_LIST = [("Rig", "Rig", ""), ("Model", "Model", ""), ("Shade", "Shade", "")]
# ----------------------------------

# --- Global storage for dynamic enum items ---
_dynamic_asset_enum_items = []

# --- Helper Functions ---
def list_assets(directory):
    """Helper to list folders (assets) in a given directory."""
    if not os.path.exists(directory):
        return []
    return [(asset, asset, "") for asset in os.listdir(directory) if os.path.isdir(os.path.join(directory, asset))]

def get_next_increment_filename(folder, base_name):
    """Find next available incremental filename like base_name_v001.blend"""
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True) # Ensure folder exists before trying to list its contents
        return f"{base_name}_v001.blend"
    existing = [f for f in os.listdir(folder) if f.startswith(base_name) and f.endswith(".blend")]
    numbers = []
    for f in existing:
        parts = f.replace(".blend", "").split("_v")
        if len(parts) > 1 and parts[-1].isdigit():
            numbers.append(int(parts[-1]))
    next_number = max(numbers, default=0) + 1
    return f"{base_name}_v{str(next_number).zfill(3)}.blend"

def ensure_directories(asset_root_abs, asset_name):
    """Ensure asset directories exist for wip, publish, and asset library."""
    # Modified paths
    wip_dir = os.path.join(asset_root_abs, "wip", "Assets", asset_name)
    publish_dir = os.path.join(asset_root_abs, "publish", "Assets", asset_name)
    assetlib_dir = os.path.join(asset_root_abs, "Asset Library") # This path remains unchanged

    os.makedirs(wip_dir, exist_ok=True)
    os.makedirs(publish_dir, exist_ok=True)
    os.makedirs(assetlib_dir, exist_ok=True)

def get_latest_version(directory, base_name):
    """Find the latest version of a .blend file based on the _v### suffix."""
    if not os.path.isdir(directory):
        return None
    latest_version = None
    latest_number = -1
    for filename in os.listdir(directory):
        if filename.startswith(base_name) and filename.endswith(".blend"):
            parts = filename.replace(".blend", "").split("_v")
            if len(parts) > 1 and parts[-1].isdigit():
                version_number = int(parts[-1])
                if version_number > latest_number:
                    latest_number = version_number
                    latest_version = filename
    return os.path.join(directory, latest_version) if latest_version else None

# --- Dynamic Enum Callbacks & Updaters ---
def get_asset_enum_items(self, context):
    """Callback for EnumProperty items to dynamically list assets."""
    global _dynamic_asset_enum_items
    # Ensure it always returns a list, even if empty or placeholder
    if not _dynamic_asset_enum_items:
        return [("NONE", "Initializing or no directory set...", "")]
    return _dynamic_asset_enum_items

def update_asset_list_and_dependent_props(self, context):
    """Called when directory_path changes. Updates the global list for asset_enum."""
    global _dynamic_asset_enum_items

    current_asset_selection = self.asset_enum

    if self.directory_path:
        abs_path = bpy.path.abspath(self.directory_path)
        # Modified scan path
        wip_scan_path = os.path.join(abs_path, "wip", "Assets")

        if not os.path.isdir(wip_scan_path):
            print(f"Asset scan: WIP Series Directory not found: {wip_scan_path}. Will be created if saving an asset.")
            _dynamic_asset_enum_items = [("NONE", "No assets (WIP folder missing/empty)", f"Path: {wip_scan_path}")]
        else:
            assets_found = list_assets(wip_scan_path)
            if not assets_found:
                _dynamic_asset_enum_items = [("NONE", "No assets found in WIP", f"No subdirectories in {wip_scan_path}")]
            else:
                _dynamic_asset_enum_items = assets_found
    else:
        _dynamic_asset_enum_items = [("NONE", "Series Directory not set", "")]

    # Attempt to restore previous selection if it's still valid
    new_selection_options = [item[0] for item in _dynamic_asset_enum_items]
    if current_asset_selection in new_selection_options:
        pass
    elif new_selection_options and new_selection_options[0] != "NONE":
        pass # Let Blender handle default selection or keep it blank if "NONE" is the first
    elif new_selection_options and new_selection_options[0] == "NONE":
        self.asset_enum = "NONE" # Explicitly set to NONE if it's the only/first option
    else: # list is completely empty (should not happen due to initialization)
        self.asset_enum = "NONE"

    self.update_asset() # Call to update asset_name and asset_full_path
    return None # Required for update functions


# --- Properties ---
class AssetSelectorProperties(PropertyGroup):
    directory_path: StringProperty(
        name="Series Directory",
        subtype='DIR_PATH',
        update=update_asset_list_and_dependent_props,
        default="z:\\",
#        update=lambda self, context: update_asset_list_and_dependent_props() #updated, remove and uncomment 124
    )

    asset_enum: EnumProperty(
        name="Asset",
        description="Select an asset from 'Series Directory Root/wip/Assets/'", # Updated description
        items=get_asset_enum_items,
        update=lambda self, context: self.update_asset()
    )

    asset_name: StringProperty(
        name="Asset Name (Manual/Selected)",
        default="",
        description="Selected asset name, or type manually to create a new asset structure",
        update=lambda self, context: self.sync_wip_path_from_manual_asset_name()
    )

    task_enum: EnumProperty(
        name="Task",
        description="Select Task",
        items=TASK_LIST,
        default=TASK_LIST[0][0] if TASK_LIST else None, # Default to first task
        update=lambda self, context: self.update_task()
    )

    task_name: StringProperty(
        name="Task Name (Manual/Selected)",
        default="",
        description="Selected task name, or type manually"
    )

    asset_wip_dir_path: StringProperty(
        name="Current Asset WIP Directory",
        default="",
        subtype='DIR_PATH',
        description="Effective WIP directory for the selected asset"
    )

    def sync_wip_path_from_manual_asset_name(self):
        """Update WIP path if asset_name is typed manually and asset_enum is NONE or different."""
        if self.asset_name and self.directory_path:
            if self.asset_enum == "NONE" or self.asset_enum != self.asset_name:
                # Modified path
                self.asset_wip_dir_path = os.path.join(bpy.path.abspath(self.directory_path), "wip", "Assets", self.asset_name)
        elif not self.asset_name and (self.asset_enum == "NONE" or not self.asset_enum):
            # If asset_name is cleared and enum is also not set, clear path
            if self.directory_path:
                # Modified path
                self.asset_wip_dir_path = os.path.join(bpy.path.abspath(self.directory_path), "wip", "Assets") # Path to general wip/Assets folder
            else:
                self.asset_wip_dir_path = ""


    def update_asset(self):
        """Auto update asset_name and WIP directory path when asset_enum changes."""
        if self.asset_enum and self.asset_enum != "NONE":
            self.asset_name = self.asset_enum
            if self.directory_path:
                # Modified path
                self.asset_wip_dir_path = os.path.join(bpy.path.abspath(self.directory_path), "wip", "Assets", self.asset_name)
            else:
                self.asset_wip_dir_path = ""
        elif self.asset_enum == "NONE":
            # If asset_enum is "NONE", asset_name might have been typed manually.
            # Rely on asset_name's own update or direct input.
            # If asset_name is also empty, clear the specific asset WIP path.
            if not self.asset_name and self.directory_path:
                # Modified path
                self.asset_wip_dir_path = os.path.join(bpy.path.abspath(self.directory_path), "wip", "Assets")
            elif self.asset_name and self.directory_path: # asset_name is manually set
                # Modified path
                self.asset_wip_dir_path = os.path.join(bpy.path.abspath(self.directory_path), "wip", "Assets", self.asset_name)
            else: # No directory path
                self.asset_wip_dir_path = ""

        self.update_task() # Also update task in case default needs to be set initially

    def update_task(self):
        """Auto update task_name when task_enum changes or asset context changes."""
        if self.task_enum:
            self.task_name = self.task_enum
        elif TASK_LIST and not self.task_name: # If task_name is empty and there are tasks, set default
            self.task_enum = TASK_LIST[0][0] # This will trigger its own update to set task_name

# --- Save Logic ---
class SaveFilesLogic:
    def __init__(self, asset_root_abs, asset_name, task_name):
        self.asset_root_abs = asset_root_abs
        self.asset_name = asset_name
        self.task_name = task_name

    def save_file(self, mode="wip", incremental=True):
        if not self.asset_name or not self.task_name:
            raise ValueError("Asset Name and Task Name cannot be empty for saving.")

        ensure_directories(self.asset_root_abs, self.asset_name)

        if mode == "wip":
            # Modified path
            target_dir = os.path.join(self.asset_root_abs, "wip", "Assets", self.asset_name)
        elif mode == "publish":
            # Modified path
            target_dir = os.path.join(self.asset_root_abs, "publish", "Assets", self.asset_name)
        elif mode == "asset_library":
            target_dir = os.path.join(self.asset_root_abs, "Asset Library")
        else:
            raise ValueError("Unknown save mode: " + mode)

        # Redundant if ensure_directories was called, but good for safety if target_dir logic changes
        os.makedirs(target_dir, exist_ok=True)

        base_name = f"{self.asset_name}_{self.task_name}"

        if incremental and mode != "asset_library":
            filename = get_next_increment_filename(target_dir, base_name)
        else:
            filename = f"{base_name}.blend"

        save_path = os.path.join(target_dir, filename)

        try:
            current_filepath = bpy.data.filepath
            is_untitled = not bpy.data.is_saved

            bpy.ops.wm.save_as_mainfile(filepath=save_path, copy=False)
            print(f"Saved to: {save_path}")
            return save_path
        except Exception as e:
            print(f"Error saving to {save_path}: {e}")
            raise

# --- Save Operators ---
class IterateSave(Operator):
    bl_idname = "smol.iterate_save"
    bl_label = "Save Incremental WIP"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.asset_selector_props
        assetname = props.asset_name.strip() if props.asset_name else (props.asset_enum if props.asset_enum != "NONE" else "")
        taskname = props.task_name.strip() if props.task_name else props.task_enum

        if not props.directory_path:
            self.report({'ERROR'}, "Series Directory Root must be set!")
            return {'CANCELLED'}
        if not assetname:
            self.report({'ERROR'}, "Asset Name must be selected or typed!")
            return {'CANCELLED'}
        if not taskname:
            self.report({'ERROR'}, "Task Name must be selected or typed!")
            return {'CANCELLED'}

        asset_root_abs = bpy.path.abspath(props.directory_path)
        if not os.path.isdir(asset_root_abs):
            try: # Try to create asset root if it doesn't exist
                os.makedirs(asset_root_abs, exist_ok=True)
                self.report({'INFO'}, f"Created Series Directory Root: {asset_root_abs}")
            except Exception as e:
                self.report({'ERROR'}, f"Series Directory Root does not exist and could not be created: {asset_root_abs} - {e}")
                return {'CANCELLED'}

        logic = SaveFilesLogic(asset_root_abs, assetname, taskname)
        try:
            saved_path = logic.save_file(mode="wip", incremental=True)
            self.report({'INFO'}, f"Saved WIP: {saved_path}")
            
            # If a new asset was created by typing a name, refresh list and select it
            asset_just_created = False
            if assetname not in [item[0] for item in _dynamic_asset_enum_items]:
                asset_just_created = True

            update_asset_list_and_dependent_props(props, context) # Refresh list
            if asset_just_created and assetname in [item[0] for item in _dynamic_asset_enum_items]:
                props.asset_enum = assetname # Select the new asset
            elif props.asset_enum == "NONE" and assetname in [item[0] for item in _dynamic_asset_enum_items]:
                props.asset_enum = assetname

        except Exception as e:
            self.report({'ERROR'}, f"Error saving WIP: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}

class PublishFiles(Operator):
    bl_idname = "smol.publish_files"
    bl_label = "Publish Incremental Version"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.asset_selector_props
        assetname = props.asset_name.strip() if props.asset_name else (props.asset_enum if props.asset_enum != "NONE" else "")
        taskname = props.task_name.strip() if props.task_name else props.task_enum

        if not props.directory_path:
            self.report({'ERROR'}, "Series Directory Root must be set!")
            return {'CANCELLED'}
        if not assetname:
            self.report({'ERROR'}, "Asset Name must be selected or typed!")
            return {'CANCELLED'}
        if not taskname:
            self.report({'ERROR'}, "Task Name must be selected or typed!")
            return {'CANCELLED'}

        asset_root_abs = bpy.path.abspath(props.directory_path)
        if not os.path.isdir(asset_root_abs):
            try:
                os.makedirs(asset_root_abs, exist_ok=True)
                self.report({'INFO'}, f"Created Series Directory Root: {asset_root_abs}")
            except Exception as e:
                self.report({'ERROR'}, f"Series Directory Root does not exist and could not be created: {asset_root_abs} - {e}")
                return {'CANCELLED'}

        logic = SaveFilesLogic(asset_root_abs, assetname, taskname)
        try:
            # Save incremental version to publish folder
            saved_path = logic.save_file(mode="publish", incremental=True)
            self.report({'INFO'}, f"Published: {saved_path}")

            # Save single non-incremental version to Asset Library (overwrite existing)
            try:
                asset_lib_path = logic.save_file(mode="asset_library", incremental=False)
                self.report({'INFO'}, f"Also saved to Asset Library: {asset_lib_path}")
            except Exception as e:
                self.report({'WARNING'}, f"Publish succeeded but saving to Asset Library failed: {str(e)}")

            asset_just_created = False
            if assetname not in [item[0] for item in _dynamic_asset_enum_items]:
                asset_just_created = True

            update_asset_list_and_dependent_props(props, context)
            if asset_just_created and assetname in [item[0] for item in _dynamic_asset_enum_items]:
                props.asset_enum = assetname
            elif props.asset_enum == "NONE" and assetname in [item[0] for item in _dynamic_asset_enum_items]:
                props.asset_enum = assetname

        except Exception as e:
            self.report({'ERROR'}, f"Error publishing file: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}

# --- Load Operators ---
class LoadLatestWIP(Operator):
    bl_idname = "smol.load_latest_wip"
    bl_label = "Load Latest WIP"

    def execute(self, context):
        props = context.scene.asset_selector_props
        assetname = props.asset_name.strip() if props.asset_name else (props.asset_enum if props.asset_enum != "NONE" else "")
        taskname = props.task_name.strip() if props.task_name else props.task_enum

        if not props.directory_path:
            self.report({'ERROR'}, "Series Directory Root must be set!")
            return {'CANCELLED'}
        if not assetname:
            self.report({'ERROR'}, "Asset Name must be selected or typed!")
            return {'CANCELLED'}
        if not taskname:
            self.report({'ERROR'}, "Task Name must be selected or typed!")
            return {'CANCELLED'}

        asset_root_abs = bpy.path.abspath(props.directory_path)
        # Modified path
        wip_dir = os.path.join(asset_root_abs, "wip", "Assets", assetname)

        if not os.path.isdir(wip_dir):
            self.report({'INFO'}, f"WIP directory for asset not found: {wip_dir}")
            return {'CANCELLED'}

        base_name = f"{assetname}_{taskname}"
        latest_file = get_latest_version(wip_dir, base_name)

        if latest_file:
            try:
                bpy.ops.wm.open_mainfile(filepath=latest_file)
                self.report({'INFO'}, f"Loaded latest WIP: {latest_file}")

                new_props = bpy.context.scene.asset_selector_props
                new_props.asset_enum = assetname # Try to set enum on new scene props
                new_props.task_enum = taskname
                update_asset_list_and_dependent_props(new_props, context) # Refresh list for new context

                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Error loading file: {str(e)}")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, f"No WIP files found for '{base_name}' in {wip_dir}")
            return {'CANCELLED'}

class LoadLatestPublish(Operator):
    bl_idname = "smol.load_latest_publish"
    bl_label = "Load Latest Publish"

    def execute(self, context):
        props = context.scene.asset_selector_props
        assetname = props.asset_name.strip() if props.asset_name else (props.asset_enum if props.asset_enum != "NONE" else "")
        taskname = props.task_name.strip() if props.task_name else props.task_enum

        if not props.directory_path:
            self.report({'ERROR'}, "Series Directory Root must be set!")
            return {'CANCELLED'}
        if not assetname:
            self.report({'ERROR'}, "Asset Name must be selected or typed!")
            return {'CANCELLED'}
        if not taskname:
            self.report({'ERROR'}, "Task Name must be selected or typed!")
            return {'CANCELLED'}

        asset_root_abs = bpy.path.abspath(props.directory_path)
        # Modified path
        publish_dir = os.path.join(asset_root_abs, "publish", "Assets", assetname)

        if not os.path.isdir(publish_dir):
            self.report({'INFO'}, f"Publish directory for asset not found: {publish_dir}")
            return {'CANCELLED'}
            
        base_name = f"{assetname}_{taskname}"
        latest_file = get_latest_version(publish_dir, base_name)

        if latest_file:
            try:
                bpy.ops.wm.open_mainfile(filepath=latest_file)
                self.report({'INFO'}, f"Loaded latest Publish: {latest_file}")

                new_props = bpy.context.scene.asset_selector_props
                new_props.asset_enum = assetname
                new_props.task_enum = taskname
                update_asset_list_and_dependent_props(new_props, context)

                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Error loading file: {str(e)}")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, f"No published files found for '{base_name}' in {publish_dir}")
            return {'CANCELLED'}

# --- Panels ---
class AssetSelectorPanel(Panel):
    bl_label = "Asset Manager" # Panel Label
    bl_idname = "VIEW3D_PT_asset_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Two Pints'

    def draw(self, context):
        layout = self.layout
        props = context.scene.asset_selector_props

        layout.prop(props, "directory_path")
        layout.separator()

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Asset:")
        row = col.row(align=True)
        row.prop(props, "asset_enum", text="")
        row.prop(props, "asset_name", text="Name")

        col = box.column(align=True)
        col.label(text="Task:")
        row = col.row(align=True)
        row.prop(props, "task_enum", text="")
        row.prop(props, "task_name", text="Name")
        layout.separator()

        layout.separator()
        col = layout.column(align=True)
        col.operator(LoadLatestWIP.bl_idname, text="Asset Load WIP", icon='FILE_FOLDER')
        col.operator(IterateSave.bl_idname, text="Asset Save WIP", icon='FILE_NEW')
        layout.separator()
        col = layout.column(align=True)
        col.operator(LoadLatestPublish.bl_idname, text="Asset Load Publish", icon='FILE_FOLDER')
        col.operator(PublishFiles.bl_idname, text="Asset Publish", icon='ASSET_MANAGER')

# --- Registration ---
_classes = [
    AssetSelectorProperties,
    IterateSave,
    PublishFiles,
    LoadLatestWIP,
    LoadLatestPublish,
    AssetSelectorPanel
]

def register():
    global _dynamic_asset_enum_items
    _dynamic_asset_enum_items = [("NONE", "Set Directory Path first", "")]

    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.asset_selector_props = PointerProperty(type=AssetSelectorProperties)


def unregister():
    global _dynamic_asset_enum_items
    
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.asset_selector_props
    _dynamic_asset_enum_items = []

if __name__ == "__main__":
    # Clean unregister attempt for testing
    try:
        # Check if a panel with this bl_idname exists (indicative of previous registration)
        if hasattr(bpy.types, AssetSelectorPanel.bl_idname.replace("_PT_", "_OT_")): # A bit of a hacky check
            unregister()
        elif bpy.context.scene.get("asset_selector_props") is not None:
            unregister()
    except Exception as e:
        print(f"Pre-unregistration error (ignored): {e}")
        if hasattr(bpy.types.Scene, 'asset_selector_props'):
            print("Force deleting bpy.types.Scene.asset_selector_props")
            del bpy.types.Scene.asset_selector_props
            
    register()
