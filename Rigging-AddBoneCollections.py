import bpy

# props color set

armature = bpy.ops.armature
props = ("Root", "Root.001", "COG.001", "COG.002", "OBJ.001", "OBJ.002", "OBJ1.001", "OBJ1.002")
#colors = (0.435294, 0.184314, 0.415686, 0.156211, 0.131012, 0.305411, 0.956863, 0.788236, 0.0470588, 0.467974, 0.296512, 0.0230151, 0.117647, 0.568627, 0.0352941, 0.165505, 0.272679, 0.0304802, 1, 0.00268805, 0, 1, 0.263096, 0.261111)

#groupIndex = 1
#colorSetIndex = 0

for index, prop in enumerate(props):
#    pairedColors = colors[colorIndex:colorIndex + 3]
#    colorSet = colorSetIndex
    armature.collection_add()
    bpy.context.object.data.collections_all["Bones"].name = prop
#    bpy.context.collection_add[index].normal = pairedColors
#    print(f"this name is {prop}")
#    print(f"Paired color is {pairedColors}")
#    print(f"Color Set Index is {index}")
#    colorIndex += 3
#    groupIndex += 1
