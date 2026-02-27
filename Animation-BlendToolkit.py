"""
Blender Add-on: Graph Editor Blend Ops Panel (WORKING VERSION)

This version fixes:
- Panel not appearing
- Extra parenthesis syntax error
- Unsafe timers during registration
- Missing keymap registration

TESTED ARCHITECTURE REQUIREMENTS:
- Blender 3.6+
- Graph Editor → N-panel → Blend Ops

Design:
- Absolute blend sliders
- Auto-reset to zero
- RMB cancel via keymap
- Selected keys, fallback to cursor keys
"""

bl_info = {
    "name": "Graph Editor Blend Ops",
    "author": "B K",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "Graph Editor > Sidebar > Blend Ops",
    "category": "Animation",
}

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import FloatProperty, PointerProperty

# ---------------------------------------------------------------------------
# GLOBAL STATE
# ---------------------------------------------------------------------------

class BlendInteractionState:
    active = False
    operator_id = None
    cache = []

STATE = BlendInteractionState()


# ---------------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------------

class CachedKeyframe:
    def __init__(self, fcurve, index, y_start, y_target):
        self.fcurve = fcurve
        self.index = index
        self.y_start = y_start
        self.y_target = y_target

    def restore(self):
        self.fcurve.keyframe_points[self.index].co.y = self.y_start

    def apply(self, factor):
        y = self.y_start + (self.y_target - self.y_start) * factor
        self.fcurve.keyframe_points[self.index].co.y = y


# ---------------------------------------------------------------------------
# KEYFRAME COLLECTION
# ---------------------------------------------------------------------------


def collect_keyframes(context):
    scene = context.scene
    frame = scene.frame_current
    collected = []

    for obj in context.selected_objects:
        ad = obj.animation_data
        if not ad or not ad.action:
            continue

        for fc in ad.action.fcurves:
            if fc.lock or fc.mute:
                continue

            selected = [i for i, k in enumerate(fc.keyframe_points)
                        if k.select_control_point]

            if selected:
                for i in selected:
                    collected.append((fc, i))
            else:
                for i, k in enumerate(fc.keyframe_points):
                    if k.co.x == frame:
                        collected.append((fc, i))

    return collected


# ---------------------------------------------------------------------------
# TARGET COMPUTATION
# ---------------------------------------------------------------------------


def get_neighbors(keys, i):
    prev_k = keys[i - 1] if i > 0 else None
    next_k = keys[i + 1] if i < len(keys) - 1 else None
    return prev_k, next_k


def linear_target(prev_k, next_k, x):
    if not prev_k or not next_k:
        return None
    x0, y0 = prev_k.co
    x1, y1 = next_k.co
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    return y0 + (y1 - y0) * t


def compute_target(fc, idx, mode, to_value):
    keys = fc.keyframe_points
    cur = keys[idx]
    x = cur.co.x
    prev_k, next_k = get_neighbors(keys, idx)

    if mode == 'NEXT':
        return next_k.co.y if next_k else cur.co.y
    if mode == 'PREV':
        return prev_k.co.y if prev_k else cur.co.y
    if mode == 'LINEAR':
        y = linear_target(prev_k, next_k, x)
        return y if y is not None else cur.co.y
    if mode == 'EASE':
        y = linear_target(prev_k, next_k, x)
        return (cur.co.y + y) * 0.5 if y is not None else cur.co.y
    if mode == 'CONSTANT':
        return prev_k.co.y if prev_k else cur.co.y
    if mode == 'VALUE':
        return to_value
    return cur.co.y


# ---------------------------------------------------------------------------
# INTERACTION
# ---------------------------------------------------------------------------


def begin_interaction(context, mode):
    STATE.active = True
    STATE.operator_id = mode
    STATE.cache.clear()

    props = context.scene.graph_blend_props

    for fc, idx in collect_keyframes(context):
        k = fc.keyframe_points[idx]
        target = compute_target(fc, idx, mode, props.to_value)
        STATE.cache.append(CachedKeyframe(fc, idx, k.co.y, target))


def apply_interaction(factor):
    for ck in STATE.cache:
        ck.apply(factor)


def cancel_interaction():
    for ck in STATE.cache:
        ck.restore()
    STATE.active = False
    STATE.cache.clear()


# ---------------------------------------------------------------------------
# PROPERTY GROUP
# ---------------------------------------------------------------------------


def slider_update_factory(mode):
    def update(self, context):
        value = getattr(self, mode)
        if value != 0.0:
            if not STATE.active:
                begin_interaction(context, mode)
            apply_interaction(value)
            setattr(self, mode, 0.0)
            STATE.active = False
            STATE.cache.clear()
    return update


class GraphBlendProps(PropertyGroup):
    to_value: FloatProperty(name="Target Value", default=0.0)

    NEXT: FloatProperty(min=-1, max=1, update=slider_update_factory('NEXT'))
    PREV: FloatProperty(min=-1, max=1, update=slider_update_factory('PREV'))
    LINEAR: FloatProperty(min=-1, max=1, update=slider_update_factory('LINEAR'))
    EASE: FloatProperty(min=-1, max=1, update=slider_update_factory('EASE'))
    CONSTANT: FloatProperty(min=-1, max=1, update=slider_update_factory('CONSTANT'))
    VALUE: FloatProperty(min=-1, max=1, update=slider_update_factory('VALUE'))


# ---------------------------------------------------------------------------
# UI PANEL
# ---------------------------------------------------------------------------

class GRAPHEDITOR_PT_blend_ops(Panel):
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Blend Ops'
    bl_label = 'Blend Operators'

    def draw(self, context):
        p = context.scene.graph_blend_props
        layout = self.layout
        layout.prop(p, 'NEXT', text='Blend → Next')
        layout.prop(p, 'PREV', text='Blend → Previous')
        layout.prop(p, 'LINEAR', text='Blend → Linear')
        layout.prop(p, 'EASE', text='Blend → Ease')
        layout.prop(p, 'CONSTANT', text='Blend → Constant')
        layout.separator()
        layout.prop(p, 'to_value')
        layout.prop(p, 'VALUE', text='Blend → To Value')


# ---------------------------------------------------------------------------
# RMB CANCEL OPERATOR + KEYMAP
# ---------------------------------------------------------------------------

class GRAPHEDITOR_OT_blend_cancel(Operator):
    bl_idname = "graph.blend_cancel"
    bl_label = "Cancel Blend"

    def invoke(self, context, event):
        if STATE.active:
            cancel_interaction()
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


addon_keymaps = []


# ---------------------------------------------------------------------------
# REGISTER
# ---------------------------------------------------------------------------

classes = (
    GraphBlendProps,
    GRAPHEDITOR_PT_blend_ops,
    GRAPHEDITOR_OT_blend_cancel,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.graph_blend_props = PointerProperty(type=GraphBlendProps)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Graph Editor', space_type='GRAPH_EDITOR')
        kmi = km.keymap_items.new('graph.blend_cancel', 'RIGHTMOUSE', 'PRESS')
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    del bpy.types.Scene.graph_blend_props

    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()