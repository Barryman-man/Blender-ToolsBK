bl_info = {
    "name": "Render Setup Menu",
    "author": "Barry Karnowski",
    "version": (0, 0, 1),
    "blender": (4, 3, 2),
    "location": "3D Viewport > Sidebar > Render Panel",
}

# give Python access to Blender's functionality
import bpy
layer_name = ['BG', 'Elements', 'Kiwicano']

class VIEW3D_PT_my_custom_panel(bpy.types.Panel):  # class naming convention ‘CATEGORY_PT_name’

    # where to add the panel in the UI
    bl_space_type = "VIEW_3D"  # 3D Viewport area (find list of values here https://docs.blender.org/api/current/bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items)
    bl_region_type = "UI"  # Sidebar region (find list of values here https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items)

    bl_category = "Render Setup_Barry"  # found in the Sidebar
    bl_label = "Render Setup_Barry"  # found at the top of the Panel

    def draw(self, context):
        """define the layout of the panel"""
        self.layout.operator('render.createlayers')
        self.layout.operator('render.setassetvis')
        self.layout.operator('render.set_render_settings')
        self.layout.operator('render.import_light_assets')
        col = self.layout.column(align=True)

# organize collections
def categorize_collection():
    element_collection = {}  # Dictionary to hold unique elements
    elementGeo_collection = {}
    bg_collection = {}       # Dictionary to hold unique background collections
    bgGeo_collection = {}
    kiwicano_collection = {}
    kiwicanoGeo_collection = {}
    shadow_collection = {}
    bg_split = {}
        
    for collection in bpy.data.collections:
        name = collection.name

        # Hardcoded exception: Add BG0110_PillSkyDay to kiwicano collections
        if name.startswith("BG0110_PillSkyDay"):
            kiwicano_collection[name] = collection
            kiwicanoGeo_collection[name] = collection
            continue
        

        if name.startswith("CH0009") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and name[-3:].isdigit():
            kiwicano_collection[name] = collection # should only contain CH0009_Kiwicano
            
        elif name.startswith("CH0009") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and ".Geo" in name:
            kiwicanoGeo_collection[name] = collection # should only contain CH0009_Kiwicano
            
        elif name.startswith("PR") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and name[-3:].isdigit():
            element_collection[name] = collection
            
        elif name.startswith("PR") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and ".Geo" in name:
            elementGeo_collection[name] = collection
            
        elif name.startswith("BG") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and name[-3:].isdigit():
            bg_collection[name] = collection
            
        elif name.startswith("BG") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and ".Geo" in name:
            bgGeo_collection[name] = collection
            
        elif name.startswith("CH") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and name[-3:].isdigit():
            element_collection[name] = collection # should contain all CH#### and PR#### collections EXCEPT for CH0009_Kiwicano
            
        elif name.startswith("CH") and len(name) > 10 and name[2:6].isdigit() and name.count("_") == 1 and name[-4] == "." and ".Geo" in name:
            elementGeo_collection[name] = collection
        
        if ".Shd" in name:
            shadow_collection[name] = collection # should only contain any *.Shd collections

    return list(element_collection.values()), list(elementGeo_collection.values()), list(bg_collection.values()), list(bgGeo_collection.values()), list(kiwicano_collection.values()), list(kiwicanoGeo_collection.values()), list(shadow_collection.values())

elements, elementsGeo, bgs, bgGeo, canos, canosGeo, shadow = categorize_collection()

class create_render_layers(bpy.types.Operator):
    """Checks if script has been run before, if not creates required render layers and organizes vis settings per asset"""
    bl_idname = "render.createlayers"
    bl_label = "Creates Render Layers"
    
    def execute(self, context):
        # state layers to check and create

        # cycle through each layer and check if any exist in scene that match layer_name
        def render_layer_exists(layer_name):
            for layer in bpy.context.scene.view_layers:
                if layer.name == layer_name:
                    return True
            return False
            
        # cancle or create layers
        for layer_name_to_check in layer_name:
            
            # cancel if any of layer_name exists in scene
            if render_layer_exists(layer_name_to_check):
                print(f"Render layer '{layer_name_to_check}' exists.")
                render_layer = bpy.context.scene.view_layers[layer_name_to_check]
                
            else:
                # create view layers
                bpy.ops.scene.view_layer_add(type='NEW')
                bpy.context.view_layer.name = layer_name_to_check
                print(f"Render layer '{layer_name_to_check}' does not exist.")
                print("will create new layers")
                
        return {'FINISHED'}

                        

class setAssetVis(bpy.types.Operator):
    """Sets all asset vis settings in created view layers"""
    bl_idname = "render.setassetvis"
    bl_label = "Sets Asset Visibility"
    
    def execute(self, context): 
        # set elements visibility
        # Elements = Visible
        # bg.bg.Geo = Visible - holdback = On
        # bg.bg.Shd = Visible
        # cano = Hidden
        # fog = Hidden
        bpy.context.window.view_layer = bpy.context.scene.view_layers['Elements']
        for elm in elements:
            for elmg in elementsGeo:
                bpy.context.view_layer.layer_collection.children[elm.name].children[elmg.name].exclude = False
                
        for bg in bgs:
            for bgg in bgGeo:
                bpy.context.view_layer.layer_collection.children[bg.name].children[bgg.name].exclude = True

        for cano in canos:
            for canog in canosGeo:
                bpy.context.view_layer.layer_collection.children[cano.name].children[canog.name].exclude = True
            
        for shd in shadow:
            for bg in bgs:
                bpy.context.view_layer.layer_collection.children[bg.name].children[shd.name].exclude = False
            
            
        # set bg vis
        # Elements = Hidden
        # bg.bg.Geo = Visible
        # bg.bg.Shd = Hidden
        # cano = Hidden
        # fog = Visible
        bpy.context.window.v
        bpy.context.window.view_layer = bpy.context.scene.view_layers['BG']
        for elm in elements:
            for elmg in elementsGeo:
                bpy.context.view_layer.layer_collection.children[elm.name].children[elmg.name].exclude = True
                
        for bg in bgs:
            for bgg in bgGeo:
                bpy.context.view_layer.layer_collection.children[bg.name].children[bgg.name].exclude = False

        for cano in canos:
            for canog in canosGeo:
                bpy.context.view_layer.layer_collection.children[cano.name].children[canog.name].exclude = False
            
        for shd in shadow:
            for bg in bgs:
                bpy.context.view_layer.layer_collection.children[bg.name].children[shd.name].exclude = True


        # set cano vis
        # Elements = Hidden
        # bg.bg.Geo = Visible - holdback = On
        # bg.bg.Shd = Hidden
        # cano = Visible
        # fog = Hidden
        bpy.context.window.v        
        bpy.context.window.view_layer = bpy.context.scene.view_layers['Kiwicano']
        for elm in elements:
            for elmg in elementsGeo:
                bpy.context.view_layer.layer_collection.children[elm.name].children[elmg.name].exclude = True
                
        for bg in bgs:
            set_collections_and_children_holdout([bg.name], holdout_value=True)
            for bgg in bgGeo:
                bpy.context.view_layer.layer_collection.children[bg.name].children[bgg.name].exclude = False
                bpy.context.view_layer.layer_collection.children[bg.name].children['Fog'].exclude = True
                bpy.context.view_layer.layer_collection.children[bg.name].exclude = False
                

        for cano in canos:
            for canog in canosGeo:
                bpy.context.view_layer.layer_collection.children[cano.name].children[canog.name].exclude = False
            
        for shd in shadow:
            for bg in bgs:
                bpy.context.view_layer.layer_collection.children[bg.name].children[shd.name].exclude = True


                
        return {'FINISHED'}
            

        # set file output

        # split filepath by '\'
        filepath = bpy.data.filepath.split('\\')


        # check to see if there are 9 elements in the file path (drive, showcode, wip/checkin/publish, Season, Episode, Sequence, Shot Code, Step, Task, Full Name
        if len(filepath) == (11):
            print("true")
        else:
            print("false")
            raise Exception ("File not saved in system. Save file in appropriate task and try again.")

        # set filepath split into variables    
        a,b,c,d,e,f,g,h,i,j,k = filepath

        # split file name (filepath.k)
        filename = k.split(".")
        fn, fe = filename

        print(fn)

        # set render file path output.
        bpy.context.scene.render.filepath = a+"\\"+b+"\\"+c+"\\"+d+"\\"+e+"\\"+f+"\\"+g+"\\"+h+"\\"+i+"\\"+j+"\\" +"Render\\"+fn+"_####.exr"

        return {'FINISHED'}
    
    

class ImportLightAssets(bpy.types.Operator):
    """Imports all assets for lighting"""
    bl_idname = "render.import_light_assets"
    bl_label = "Import Lighting Assets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        blend_file_path = "X:\KWI\KIWI_AssetLibrary\SetProps\Materials\WorldLighting_Day.blend"

        with bpy.data.libraries.load(blend_file_path, link=True) as (data_from, data_to):
            data_to.worlds = data_from.worlds
            data_to.objects = data_from.objects
            
        scene = bpy.context.scene

        for obj in data_to.objects:
            if obj is None:
                continue
            
            scene.collection.objects.link(obj)
            
        for wor in data_to.worlds:
            if wor is None:
                continue
            
            scene.world = wor
        return {'FINISHED'}



class SetRenderSettings(bpy.types.Operator):
    """Sets render settings in scene"""
    bl_idname = "render.set_render_settings"
    bl_label = "Set Render Settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):
        # set "ViewLayer" to not render
        bpy.data.scenes["Scene"].view_layers["ViewLayer"].use = False
        
        # set render layer AOV's
        for layer in layer_name:
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_combined = True
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_z = False
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_mist
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_position
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_normal
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_vector
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_uv
            bpy.data.scenes["Scene"].view_layers[layer].cycles.denoising_store_passes = False
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_object_index = False
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_material_index = False
            bpy.data.scenes["Scene"].view_layers[layer].pass_alpha_threshold = 0.5
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_diffuse_direct
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_diffuse_indirect
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_diffuse_color
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_glossy_direct
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_glossy_indirect
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_glossy_color
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_transmission_direct
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_transmission_indirect
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_transmission_color
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_emit
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_environment
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_ambient_occlusion
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_ambient_occlusion
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_cryptomatte_object
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_cryptomatte_material
            bpy.data.scenes["Scene"].view_layers[layer].use_pass_cryptomatte_asset
        
        






    
        # render settings
        bpy.context.scene.cycles.preview_samples = 0
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.feature_set = 'SUPPORTED'
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.use_adaptive_sampling = True
        bpy.context.scene.cycles.adaptive_threshold = 0.01
        bpy.context.scene.cycles.samples = 64
        bpy.context.scene.cycles.adaptive_min_samples = 0
        bpy.context.scene.cycles.time_limit = 0
        bpy.context.scene.cycles.use_denoising = True
        bpy.context.scene.cycles.denoiser = 'OPTIX'
        bpy.context.scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        bpy.context.scene.cycles.use_light_tree = True
        bpy.context.scene.cycles.sampling_pattern = 'AUTOMATIC'
        bpy.context.scene.cycles.seed = 0
        bpy.context.scene.cycles.sample_offset = 0
        bpy.context.scene.cycles.min_light_bounces = 0
        bpy.context.scene.cycles.min_transparent_bounces = 0
        bpy.context.scene.cycles.max_bounces = 12
        bpy.context.scene.cycles.diffuse_bounces = 4
        bpy.context.scene.cycles.glossy_bounces = 4
        bpy.context.scene.cycles.transmission_bounces = 12
        bpy.context.scene.cycles.volume_bounces = 0
        bpy.context.scene.cycles.transparent_max_bounces = 8
        bpy.context.scene.cycles.sample_clamp_direct = 0
        bpy.context.scene.cycles.sample_clamp_indirect = 10
        bpy.context.scene.cycles.blur_glossy = 1
        bpy.context.scene.cycles.caustics_refractive = False
        bpy.context.scene.cycles.caustics_reflective = False
        bpy.context.scene.cycles.use_fast_gi = False
        bpy.context.scene.cycles.volume_step_rate = 1
        bpy.context.scene.cycles.volume_preview_step_rate = 1
        bpy.context.scene.cycles.volume_max_steps = 4096
        bpy.context.scene.cycles_curves.shape = 'RIBBONS'        
        bpy.context.scene.cycles_curves.subdivisions = 2
        bpy.context.scene.render.hair_type = 'STRAND'
        bpy.context.scene.render.hair_subdiv = 0
        bpy.context.scene.render.use_simplify = False
        bpy.context.scene.render.simplify_subdivision = 1
        bpy.context.scene.render.simplify_child_particles = 1
        bpy.context.scene.cycles.texture_limit = '512'
        bpy.context.scene.render.simplify_volumes = 1
        bpy.context.scene.render.use_simplify_normals = False
        bpy.context.scene.render.simplify_subdivision_render = 4
        bpy.context.scene.render.simplify_child_particles_render = 1
        bpy.context.scene.cycles.texture_limit_render = '4096'
        bpy.context.scene.cycles.use_camera_cull = False
        bpy.context.scene.cycles.use_distance_cull = False
        bpy.context.scene.render.use_motion_blur = False
        bpy.context.scene.cycles.film_exposure = 1
        bpy.context.scene.cycles.pixel_filter_type = 'BLACKMAN_HARRIS'
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.cycles.film_transparent_glass = False
        bpy.context.scene.render.compositor_device = 'GPU'
        bpy.context.scene.render.compositor_precision = 'FULL'
        bpy.context.scene.render.threads_mode = 'AUTO'
        bpy.context.scene.cycles.use_auto_tile = True
        bpy.context.scene.cycles.tile_size = 32
        bpy.context.scene.render.use_persistent_data = True
        bpy.context.scene.render.preview_pixel_size = '4'
        bpy.context.scene.display_settings.display_device = 'sRGB'
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.view_settings.look = 'None'
        bpy.context.scene.view_settings.exposure = 0
        bpy.context.scene.view_settings.gamma = 1
        bpy.context.scene.sequencer_colorspace_settings.name = 'sRGB'
        bpy.context.scene.render.use_sequencer = False
        bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        bpy.context.scene.render.use_overwrite = True
        bpy.context.scene.render.use_placeholder = False

        
                # set file output

        # split filepath by '\'
        filepath = bpy.data.filepath.split('\\')


        # check to see if there are 9 elements in the file path (drive, showcode, wip/checkin/publish, Season, Episode, Sequence, Shot Code, Step, Task, Full Name
        if len(filepath) == (11):
            print("true")
        else:
            print("false")
            raise Exception ("File not saved in system. Save file in appropriate task and try again.")

        # set filepath split into variables    
        a,b,c,d,e,f,g,h,i,j,k = filepath

        # split file name (filepath.k)
        filename = k.split(".")
        fn, fe = filename

        print(fn)

        # set render file path output.
        bpy.context.scene.render.filepath = a+"\\"+b+"\\"+c+"\\"+d+"\\"+e+"\\"+f+"\\"+g+"\\"+h+"\\"+i+"\\"+j+"\\" +"Render\\"+fn+".png"

    
        return{'FINISHED'}
    
    
 
# recursive hold out script    
def set_collections_and_children_holdout(collection_names, holdout_value=True):
    """
#    Sets the holdout property for a list of collections and all their children
#    in the current view layer.
#    Args:
#        collection_names (list of str): A list of collection names to target.
#        holdout_value (bool): The holdout value to set (True or False). Defaults to True.
    """
    def set_holdout_recursive(collection, layer_collection, value):
        """Recursive function to set holdout for a collection and its children."""
        layer_col = layer_collection.children.get(collection.name)
        if layer_col:
            layer_col.holdout = value
            for child in collection.children:
                set_holdout_recursive(child, layer_col, value)
    view_layer = bpy.context.view_layer
    master_layer_collection = view_layer.layer_collection
    for collection_name in collection_names:
        collection = bpy.data.collections.get(collection_name)
        if collection:
            set_holdout_recursive(collection, master_layer_collection, holdout_value)
            print(f"Set holdout '{holdout_value}' for collection '{collection_name}' and its children.")
        else:
            print(f"Collection '{collection_name}' not found.")



        
def register():
    bpy.utils.register_class(VIEW3D_PT_my_custom_panel)
    bpy.utils.register_class(SetRenderSettings)
    bpy.utils.register_class(create_render_layers)
    bpy.utils.register_class(setAssetVis)
    bpy.utils.register_class(ImportLightAssets)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_my_custom_panel)
    bpy.utils.unregister_class(SetRenderSettings)
    bpy.utils.unregister_class(create_render_layers)
    bpy.utils.unregister_class(setAssetVis)
    bpy.utils.unregister_class(ImportLightAssets)


if __name__ == "__main__":
    register()
