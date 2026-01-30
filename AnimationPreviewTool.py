import bpy

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
# a = drive
# b = showcode
# c = wip/checking/publish
# d = shots
# e = season
# d = episode
# e = episode/sequence
# f = shotcode
# g = step
# h = task
# i = 
a,b,c,d,e,f,g,h,i,j,k = filepath

# split file name (filepath.k)
filename = k.split(".")
fn, fe = filename

# concenate file name
fullpath = a+"\\"+b+"\\"+c+"\\"+d+"\\"+e+"\\"+f+"\\"+g+"\\"+h+"\\"+i+"\\"+j+"\\"

print(fn)

# set render file path output.
bpy.context.scene.render.filepath = fullpath +"Playblasts\\"+fn+".mov"
bpy.data.scenes["Scene"].render.filepath
# set render options

# define variables for Default Blender Load + Raytracing

renderEngineIS = "BLENDER_EEVEE_NEXT"
samplesIS = 128
shadowsIS = True
shadowRaysIS = 1
shadowStepsIS =6
shadowVolumeIS = False
shadowVolumeStepsIS = 16
shadowResolutionIS = 1.0
shadowLightThreshIS = 0.010
clampingSurfDLIS = 0.0
clampingSurfILIS = 10.00
clampingVolDLIS = 0.00
clampingVolILIS = 0.00
raytracingIS = True
raytracingMethodIS = "SCREEN"
raytracingRes = "2"
raytracingSTPrecision = 0.250
raytracingSTThickness = 0.2
raytracingDenoisIS = True
raytracingDenoiseSRIS = True
raytracingDenoiseTAIS = True
raytracingDenoiseBF = True
raytracingGIIS = True
raytracingGIThreshIS = 0.5
raytracingGIMethodIS = "GLOBAL_ILLUMINATION"
raytracingGIResolutionIS = "2"
raytracingGIRaysIS = 2
raytracingGISteps = 8
raytracingGIPrecisionIS = 0.250
raytracingGIDistanceIS = 0
raytracingGINearIS = 0.25
raytracingGIFarIS = 0.785398
raytracingGIBiasIS = 0.05
volumesResolution = "8"
volumesSteps = 64
volumesDistribution = 0.800
volumesMaxDepth = 16
volumesStart = 0.1
volumesEnd = 100
dofMaxSizeIS = 100
dofThreshIS = 1.00
dofRejectionIS = 10.00
dofJitterIS = False
dofJitterBlurIS = 5
motionBlurIS = False
motionBlurPosition = "CENTER"
motionBlurShutter = 0.50
motionBlurBias = 100
motionBlurMax = 32
motionBlurSteps = 1
filmFilter = 1.50
filmTransparentIS = False
filmOverscanIS = False
filmOverscan = 3.00
performanceShadowPool = "512"
performanceLighProbes = "16"
performanceCompositorDevice = "GPU"
performanceCompositorPrecision = "AUTO"
colorManagementDisplayDevice = "sRGB"
colorManagementTransform = "Standard"
colorManagementLook = "None"
colorManagementExposure = 0.000
colorManagementGamma = 1.000
colorManagementSequencer = "sRGB"
colorManagementWhiteBalanceIS = False
colorManagementTemp = 6500
colorManagementTint = 10.0
renderuse_sequencer = False
simplify = 6

# set render settings based on above variables
bpy.data.scenes["Scene"].render.engine = renderEngineIS
bpy.data.scenes["Scene"].eevee.taa_render_samples = samplesIS
bpy.data.scenes["Scene"].eevee.use_shadows = shadowsIS
bpy.data.scenes["Scene"].eevee.shadow_ray_count = shadowRaysIS
bpy.data.scenes["Scene"].eevee.shadow_step_count = shadowStepsIS
bpy.data.scenes["Scene"].eevee.use_volumetric_shadows = shadowVolumeIS
bpy.data.scenes["Scene"].eevee.volumetric_shadow_samples = shadowVolumeStepsIS
bpy.data.scenes["Scene"].eevee.shadow_resolution_scale = shadowResolutionIS 
bpy.data.scenes["Scene"].eevee.light_threshold = shadowLightThreshIS
bpy.data.scenes["Scene"].eevee.clamp_surface_direct = clampingSurfDLIS
bpy.data.scenes["Scene"].eevee.clamp_surface_indirect = clampingSurfILIS
bpy.data.scenes["Scene"].eevee.clamp_volume_direct = clampingVolDLIS
bpy.data.scenes["Scene"].eevee.clamp_volume_indirect = clampingVolILIS
bpy.data.scenes["Scene"].eevee.use_raytracing = raytracingIS
bpy.data.scenes["Scene"].eevee.ray_tracing_method = raytracingMethodIS
bpy.data.scenes["Scene"].eevee.ray_tracing_options.resolution_scale = raytracingRes
bpy.data.scenes["Scene"].eevee.ray_tracing_options.screen_trace_quality = raytracingSTPrecision
bpy.data.scenes["Scene"].eevee.ray_tracing_options.screen_trace_thickness = raytracingSTThickness
bpy.data.scenes["Scene"].eevee.ray_tracing_options.use_denoise = raytracingDenoisIS
bpy.data.scenes["Scene"].eevee.ray_tracing_options.denoise_spatial = raytracingDenoiseSRIS
bpy.data.scenes["Scene"].eevee.ray_tracing_options.denoise_temporal = raytracingDenoiseTAIS
bpy.data.scenes["Scene"].eevee.ray_tracing_options.denoise_bilateral = raytracingDenoiseBF
bpy.data.scenes["Scene"].eevee.use_fast_gi = raytracingGIIS
bpy.data.scenes["Scene"].eevee.ray_tracing_options.trace_max_roughness = raytracingGIThreshIS
bpy.data.scenes["Scene"].eevee.fast_gi_method = raytracingGIMethodIS
bpy.data.scenes["Scene"].eevee.fast_gi_resolution = raytracingGIResolutionIS
bpy.data.scenes["Scene"].eevee.fast_gi_ray_count = raytracingGIRaysIS
bpy.data.scenes["Scene"].eevee.fast_gi_step_count = raytracingGISteps
bpy.data.scenes["Scene"].eevee.fast_gi_quality = raytracingGIPrecisionIS
bpy.data.scenes["Scene"].eevee.fast_gi_distance = raytracingGIDistanceIS
bpy.data.scenes["Scene"].eevee.fast_gi_thickness_near = raytracingGINearIS
bpy.data.scenes["Scene"].eevee.fast_gi_thickness_far = raytracingGIFarIS
bpy.data.scenes["Scene"].eevee.fast_gi_bias = raytracingGIBiasIS
bpy.data.scenes["Scene"].eevee.volumetric_tile_size = volumesResolution
bpy.data.scenes["Scene"].eevee.volumetric_samples = volumesSteps
bpy.data.scenes["Scene"].eevee.volumetric_sample_distribution = volumesDistribution
bpy.data.scenes["Scene"].eevee.volumetric_ray_depth = volumesMaxDepth 
bpy.data.scenes["Scene"].eevee.volumetric_start = volumesStart
bpy.data.scenes["Scene"].eevee.volumetric_end = volumesEnd
bpy.data.scenes["Scene"].eevee.bokeh_max_size = dofMaxSizeIS
bpy.data.scenes["Scene"].eevee.bokeh_threshold = dofThreshIS
bpy.data.scenes["Scene"].eevee.bokeh_neighbor_max = dofRejectionIS
bpy.data.scenes["Scene"].eevee.use_bokeh_jittered = dofJitterIS
bpy.data.scenes["Scene"].eevee.bokeh_overblur = dofJitterBlurIS
bpy.data.scenes["Scene"].render.use_motion_blur = motionBlurIS
bpy.data.scenes["Scene"].render.motion_blur_position = motionBlurPosition
bpy.data.scenes["Scene"].render.motion_blur_shutter = motionBlurShutter
bpy.data.scenes["Scene"].eevee.motion_blur_depth_scale = motionBlurBias
bpy.data.scenes["Scene"].eevee.motion_blur_max = motionBlurMax
bpy.data.scenes["Scene"].eevee.motion_blur_steps = motionBlurSteps
bpy.data.scenes["Scene"].render.filter_size = filmFilter
bpy.data.scenes["Scene"].render.film_transparent = filmTransparentIS
bpy.data.scenes["Scene"].eevee.use_overscan = filmOverscanIS
bpy.data.scenes["Scene"].eevee.overscan_size = filmOverscan
bpy.data.scenes["Scene"].eevee.shadow_pool_size = performanceShadowPool
bpy.data.scenes["Scene"].eevee.gi_irradiance_pool_size = performanceLighProbes
bpy.data.scenes["Scene"].render.compositor_device = performanceCompositorDevice
bpy.data.scenes["Scene"].render.compositor_precision = performanceCompositorPrecision
bpy.data.scenes["Scene"].display_settings.display_device = colorManagementDisplayDevice
bpy.data.scenes["Scene"].view_settings.view_transform = colorManagementTransform
bpy.data.scenes["Scene"].view_settings.look = colorManagementLook
bpy.data.scenes["Scene"].view_settings.exposure = colorManagementExposure
bpy.data.scenes["Scene"].view_settings.gamma = colorManagementGamma
bpy.data.scenes["Scene"].sequencer_colorspace_settings.name = colorManagementSequencer
bpy.data.scenes["Scene"].view_settings.white_balance_temperature = colorManagementWhiteBalanceIS
bpy.data.scenes["Scene"].view_settings.white_balance_temperature = colorManagementTemp
bpy.data.scenes["Scene"].view_settings.white_balance_tint = colorManagementTint
bpy.data.scenes["Scene"].render.simplify_subdivision_render = simplify
#output
bpy.data.scenes["Scene"].render.resolution_x = 1920
bpy.data.scenes["Scene"].render.resolution_y = 1080
bpy.data.scenes["Scene"].render.resolution_percentage = 100
bpy.data.scenes["Scene"].render.pixel_aspect_x = 1.000
bpy.data.scenes["Scene"].render.pixel_aspect_y = 1.000
bpy.data.scenes["Scene"].render.fps = 24
bpy.data.scenes["Scene"].render.use_file_extension = True
bpy.data.scenes["Scene"].render.image_settings.file_format = 'FFMPEG'

bpy.data.scenes["Scene"].render.ffmpeg.format = 'QUICKTIME'
bpy.data.scenes["Scene"].render.ffmpeg.codec = 'H264'
bpy.data.scenes["Scene"].render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
bpy.data.scenes["Scene"].render.ffmpeg.audio_codec = 'AAC'


# set current camera
bpy.context.scene.camera = bpy.data.objects[h + ".Camera"]

# playblast

C = bpy.context

for area in C.screen.areas:
    if area.type == 'VIEW_3D':
        # check to see if view port camera is set to scene camera.
        # this is currently looking through each 3d view and checking if the SCENE camera is set and returning True both time. Need to change so that it checks the 3d viewport for the scene camera being activated and cycling through until it finds one.
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        #if C.scene.camera == bpy.data.objects["Camera"]:
        print("True")
        with C.temp_override(area=area):
                C.space_data.shading.type = 'MATERIAL'
                bpy.ops.render.opengl(animation=True)
        break
    else:
        print("false")
