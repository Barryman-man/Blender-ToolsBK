import bpy
from pathlib import Path

# --- Configuration ---
SOURCE_NODE_TREE_NAMES = [
    "Daytime.CompTree",
    "Dusk.CompTree",
    "Nighttime.CompTree"
]

def build_output_paths(context):
    """Derive output directory and file-slot path from the .blend name and render base path."""
    blend_path = Path(bpy.data.filepath)
    stem_parts = blend_path.stem.split("_")

    if len(stem_parts) < 7:
        raise ValueError("Blend filename must contain at least 7 underscore-separated parts.")

    aa, bb, cc, dd, ee, ff, gg = stem_parts[:7]
    ver_token = gg

    # slot subpath: AA_BB_CC_DD_EE_FF_v001.####.png
    file_slot_name = f"{aa}_{bb}_{cc}_{dd}_{ee}_{ff}_{ver_token}.####.png"

    # base render path (resolve relative // paths)
    render_base = Path(bpy.path.abspath(context.scene.render.filepath))

    # directory name: AA_BB_CC_DD_v001
    dir_name = f"{aa}_{bb}_{cc}_{dd}_{ver_token}"
    output_dir = render_base / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    return str(output_dir), file_slot_name


def find_source_group_node(tree):
    for node in tree.nodes:
        if node.type == 'GROUP' and getattr(node, "node_tree", None):
            if node.node_tree.name in SOURCE_NODE_TREE_NAMES:
                return node
    return None


def find_or_create_file_output_node(tree, source_node):
    """Reuse existing OUTPUT_FILE node if present; otherwise create one."""
    for node in tree.nodes:
        if node.type == 'OUTPUT_FILE':
            print("Reusing existing File Output node.")
            return node

    file_output_node = tree.nodes.new(type='CompositorNodeOutputFile')
    # place it to the right of source
    file_output_node.location.x = source_node.location.x + source_node.width + 150
    file_output_node.location.y = source_node.location.y
    print("Created a new File Output node.")
    return file_output_node


def setup_file_output():
    """Main function you can run directly from the Scripting editor."""
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    if not tree:
        print("No compositor node tree found.")
        return

    source_node = find_source_group_node(tree)
    if not source_node:
        print(f"No group node found using: {', '.join(SOURCE_NODE_TREE_NAMES)}")
        return

    try:
        output_dir, file_slot_name = build_output_paths(bpy.context)
    except Exception as ex:
        print(f"Output path build failed: {ex}")
        return

    file_output_node = find_or_create_file_output_node(tree, source_node)

    # update settings
    file_output_node.base_path = output_dir
    file_output_node.format.file_format = 'PNG'

    # reset slots
    while file_output_node.file_slots:
        file_output_node.file_slots.remove(file_output_node.file_slots[0])
    slot = file_output_node.file_slots.new("Output")
    slot.path = file_slot_name

    if not source_node.outputs:
        print(f"Source node '{source_node.name}' has no outputs.")
        return

    # clear old links
    for link in list(tree.links):
        if link.to_node == file_output_node:
            tree.links.remove(link)

    tree.links.new(source_node.outputs[0], file_output_node.inputs[0])

    print(f"✅ File Output ready: {output_dir}/{file_slot_name}")


# --- Auto-run when you hit "Run Script" ---
if __name__ == "__main__":
    setup_file_output()
