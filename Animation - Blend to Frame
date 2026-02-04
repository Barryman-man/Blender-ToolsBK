import bpy
from bpy.props import FloatProperty, IntProperty

class GRAPH_OT_blend_to_frame(bpy.types.Operator):
    """Interactively blend selected keyframes to the value at the current playhead frame"""
    bl_idname = "graph.blend_to_frame"
    bl_label = "Blend to Current Frame"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    factor: FloatProperty(
        name="Factor",
        description="Blend factor (0 = original, 1 = target frame)",
        default=0.0,
        min=0.0,  # Hard limit minimum
        max=1.0   # Hard limit maximum
    )

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            # Calculate sensitivity: move 200 pixels for 100% blend
            delta = (event.mouse_region_x - self.init_mouse_x) / 200.0
            self.factor = delta
            self.execute(context)
            context.area.header_text_set(f"Blend Factor: {self.factor:.3f} (Target Frame: {self.target_frame})")
            
        elif event.type in {'LEFTMOUSE', 'RET'}:
            context.area.header_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Reset values on cancel
            self.factor = 0.0
            self.execute(context)
            context.area.header_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type != 'GRAPH_EDITOR':
            self.report({'WARNING'}, "Operator must be used in the Graph Editor")
            return {'CANCELLED'}

        self.target_frame = context.scene.frame_current
        self.init_mouse_x = event.mouse_region_x
        
        # Store initial state: mapping keyframe objects to their original Y values
        self.original_data = []
        
        for fcurve in context.selected_editable_fcurves:
            target_val = fcurve.evaluate(self.target_frame)
            keys = []
            for kp in fcurve.keyframe_points:
                if kp.select_control_point:
                    # Store (keypoint_reference, original_y_value, target_y_value)
                    keys.append([kp, kp.co[1], target_val])
            
            if keys:
                self.original_data.append(keys)

        if not self.original_data:
            self.report({'WARNING'}, "No keyframes selected")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # The Lerp Math: Original + (Target - Original) * Factor
        for curve_keys in self.original_data:
            for kp_data in curve_keys:
                kp, orig_y, target_y = kp_data
                blend_val = orig_y + (target_y - orig_y) * self.factor
                kp.co[1] = blend_val
                
                # Optional: Update handles to prevent "kinking" the curve
                kp.handle_left[1] += (blend_val - kp.co[1]) # Simple offset
                kp.handle_right[1] += (blend_val - kp.co[1])

        # Force UI refresh
        context.area.tag_redraw()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GRAPH_OT_blend_to_frame)

def unregister():
    bpy.utils.unregister_class(GRAPH_OT_blend_to_frame)

if __name__ == "__main__":
    register()
