import bpy
rig = bpy.data.objects["rig"]
#get pose bone for Left
driven_objL = 'upperElbowPivot.R', 'lowerElbowPivot.R', 'upperArmPivot.R', 'hipPivot.R', 'kneePivot1.R'      #array of left bones to drive
driver_objL = 'DEF-middleArmDriver.R', 'DEF-lowerArmDriver.R', 'DEF-upperArmDriver.R', 'DEF-thigh.R', 'DEF-shin.R'

#driver_objL = 'pose.bones["DEF-middleArmDriver.R"]', 'pose.bones["DEF-lowerArmDriver.R"]', 'pose.bones["DEF-upperArmDriver.R"]', 'pose.bones["DEF-thigh.R"]', 'pose.bones["DEF-shin.R"]'

#driver_objL = 'DEF-middleArmDriver.R"]["DEF-lowerArmDriver.R"]'                              #left driver object
#driven_objR = 'eyeBlink.001.R', 'eyeBlink.002.R', 'eyeBlink.002_end.R'      #array of right bones to drive
#driver_objR = 'pose.bones["eye.R"]["Blink.R"]'                              #right driver object

#add drivers (loop) for Left
for i, driven_obj_nameL in enumerate (driven_objL):                          #loop start for Left side - for each object in the driven_obj array, set that to the variable "i". enumerate indexes the array and assigns it a number to loop through
    for y, driver_obj_nameL in enumerate (driver_objL):
        driven_bone = rig.pose.bones.get(driven_obj_nameL)                      #driven bone is the rig variable  plus the pose.bones.get for the driven bone in the array. This sets the current object context
        driver_rotx = driven_bone.driver_add('rotation_euler', 0)                      #adds driver to scale x

    
        #driver modificationsx
        var = driver_rotx.driver.variables.new ()                             #creates a new input variable and creates a variable for it called "var"
        expvar = driver_rotx.driver
        driver_rotx.driver.type = "SCRIPTED"                                   #sets driver type to average
        var.type = "TRANSFORMS" 


        var.name = "Screw_Turn" 
        expvar.expression = "Screw_Turn*8"
        var.targets[0].transform_type = "ROT_X"
        bpy.types.DriverVariable.rotation_mode = "AUTO"
        bpy.types.DriverVariable.transform_space = "WORLD_SPACE"                                                 #sets the input vriable name to "blink"
        var.targets[0].id = rig                                                 #sets the target for the input variable to the rig variable
        var.targets[0].bone_target = driver_obj_nameL                                  #sets the object in target for the input variable to the driver object variable
   
""" 
    #driver modificationsz the exact same as driver modifcationsx
    driver_scalez.driver.type = "AVERAGE"
    var = driver_scalez.driver.variables.new ()
    var.name = "blink"
    var.targets[0].id = rig
    var.targets[0].data_path = driver_objL
    
for i, driven_obj_nameR in enumerate(driven_objR):
    driven_bone = rig.pose.bones.get(driven_obj_nameR)
    driver_scalex = driven_bone.driver_add('scale', 0)
    driver_scalez = driven_bone.driver_add('scale', 2)
    
    #driver modificationsx
    driver_scalex.driver.type = "AVERAGE"
    var = driver_scalex.driver.variables.new ()
    var.name = "blink"
    var.targets[0].id = rig
    var.targets[0].data_path = driver_objR
    
    #driver modificationsz
    driver_scalez.driver.type = "AVERAGE"
    var = driver_scalez.driver.variables.new ()
    var.name = "blink"
    var.targets[0].id = rig
    var.targets[0].data_path = driver_objR
    
    
    
    # driver sets
# right arm
upperElbowPivot.R
DEF-middleArmDriver.R

lowerElbowPivot.R
DEF-lowerArmDriver.R

upperArmPivot.R
DEF-upperArmDriver.R

# left arm

# right leg
hipPivot.R
DEF-thigh.R

kneePivot1.R
DEF-shin.R

# left leg
"""
