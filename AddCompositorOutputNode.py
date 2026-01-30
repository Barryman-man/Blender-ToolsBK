import bpy
import os # Import the os module for path manipulation

def setup_compositor_file_output():
    """
    Sets up a File Output node in the compositor, connecting it to a
    specified group output node and configuring its path and format.
    """

    # Ensure we are in the compositor and use nodes
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    # --- Debugging Compositor Nodes ---
    print("--- Debugging Compositor Nodes (Full Scan) ---")
    if not tree.nodes:
        print("No nodes found in the current compositor tree.")
    else:
        for node in tree.nodes:
            print(f"DEBUG: Node Name: '{node.name}', Node Type: '{node.type}'")
            # Check for both 'NODE_GROUP' and 'GROUP' as valid types for a group node
            if node.type == 'NODE_GROUP' or node.type == 'GROUP':
                if node.node_tree:
                    print(f"DEBUG:   -> Group Definition Name (node.node_tree.name): '{node.node_tree.name}'")
                else:
                    print(f"DEBUG:   -> Node Group instance '{node.name}' has no linked node_tree (definition).")
            else:
                print(f"DEBUG:   (Not a recognized NODE_GROUP type, skipping group definition check)")
    print("--- End Debugging Compositor Nodes (Full Scan) ---")
    # --- End Debugging Compositor Nodes ---


    # Define the potential target node group names (both definition and instance names)
    target_names = [
        "Daytime.CompTree",
        "Nighttime.CompTree",
        "Dusktime.CompTree"
    ]

    # Find the first available target group output node instance in the compositor
    target_output_node = None
    for node in tree.nodes:
        # Check if the node is a group node (an instance of a node group), handling both type representations
        if node.type == 'NODE_GROUP' or node.type == 'GROUP':
            # Check if the name of the *definition* of the node group matches a target,
            # OR if the *instance name* of the node in the compositor matches a target.
            # We also ensure node.node_tree exists before accessing its name.
            if (node.node_tree and node.node_tree.name in target_names) or (node.name in target_names):
                target_output_node = node
                # Print the relevant name that caused the match
                matched_by = "instance name" if node.name in target_names else "definition name"
                print(f"Found target node group instance: '{node.name}' (definition: '{node.node_tree.name if node.node_tree else 'N/A'}') - Matched by: {matched_by}")
                break

    if not target_output_node:
        print(f"Error: None of the specified target node group definitions or instance names ({', '.join(target_names)}) found as instances in the compositor.")
        return

    # Check if a File Output node already exists to avoid duplicates
    file_output_node = None
    for node in tree.nodes:
        if node.type == 'OUTPUT_FILE' and node.name == "RenderFileOutput":
            file_output_node = node
            print("Existing File Output node 'RenderFileOutput' found. Updating it.")
            break

    # If no existing node, create a new File Output node
    if not file_output_node:
        file_output_node = tree.nodes.new(type='CompositorNodeOutputFile')
        file_output_node.name = "RenderFileOutput"
        print("New File Output node 'RenderFileOutput' created.")

    # Get the scene's current render output path
    full_render_filepath = bpy.data.scenes['Scene'].render.filepath

    # --- Start of logic for base path and subpath ---

    # Get the original filename (e.g., 'KWI_003_SQ01_0130_Render_Ready_v002_####.exr')
    original_filename_with_ext = os.path.basename(full_render_filepath)

    # Split the filename and extension (e.g., 'KWI_003_SQ01_0130_Render_Ready_v002_####')
    filename_without_ext, _ = os.path.splitext(original_filename_with_ext)

    # Create the folder name by removing '_####' from the filename
    # Example: "KWI_003_SQ01_0130_Render_Ready_v002_####" -> "KWI_003_SQ01_0130_Render_Ready_v002"
    folder_name_from_file = filename_without_ext.replace('_####', '')

    # Extract the directory containing 'exr' (e.g., 'X:\...\v002\exr')
    render_directory = os.path.dirname(full_render_filepath)

    # Go up one level to get the 'v002' directory (e.g., 'X:\...\v002')
    version_directory = os.path.dirname(render_directory)

    # Construct the new base path, adding the folder derived from the filename
    # The empty string as the last argument ensures a trailing slash.
    # Example: 'X:\...\v002' + 'KWI_003_SQ01_0130_Render_Ready_v002' + '\'
    new_base_path = os.path.join(version_directory, folder_name_from_file, "")

    # Set the base path for the File Output node
    file_output_node.base_path = new_base_path
    print(f"File Output base directory set to: {new_base_path}")

    # Construct the new subpath with the PNG extension and the '.####' sequence
    # This specifically targets the sequence part before the frame numbers for the subpath.
    corrected_filename_portion = filename_without_ext.replace('_####', '.####')
    new_subpath = f"{corrected_filename_portion}.png"

    # Set the subpath for the first file slot (default output)
    if file_output_node.file_slots:
        file_output_node.file_slots[0].path = new_subpath
        print(f"File Output subpath set to: {new_subpath}")
    else:
        print("Warning: No file slots found on the File Output node. Cannot set subpath.")

    # --- End of logic ---

    # Set the file format to PNG (ensures node's internal settings are correct)
    file_output_node.format.file_format = 'PNG'
    file_output_node.format.color_mode = 'RGBA' # Usually good for PNGs

    # Position the new node (optional, for better layout)
    file_output_node.location = (target_output_node.location.x + 300, target_output_node.location.y)

    # Connect the output of the target group node to the input of the File Output node
    if target_output_node.outputs.get("Image") and file_output_node.inputs.get("Image"):
        # Check if a link already exists to prevent duplicates
        links_exist = False
        for link in tree.links:
            if link.from_node == target_output_node and link.to_node == file_output_node:
                links_exist = True
                print("Link already exists between target node and File Output node.")
                break
        if not links_exist:
            tree.links.new(target_output_node.outputs["Image"], file_output_node.inputs["Image"])
            print("Successfully linked target node to File Output node.")
    else:
        print("Warning: Could not find 'Image' output on target node or 'Image' input on File Output node.")


# Call the function to run the script
if __name__ == "__main__":
    setup_compositor_file_output()
