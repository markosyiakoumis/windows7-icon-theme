import os
import math
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

nominal_size = 32
cursors = {
    "default": {
        "hotspot": (1, 3),
        "aliases": ["arrow", "dnd-move", "left_ptr"]
    },
    "ew-resize": {
        "hotspot": (11, 4),
        "aliases": ["sb_h_double_arrow"]
    },
    "help": {
        "hotspot": (1, 3),
        "aliases": ["question_arrow"]
    },
    "move": {
        "hotspot": (11, 11),
        "aliases": ["fleur"]
    },
    "nesw-resize": {
        "hotspot": (8, 8),
        "aliases": ["bottom_left_corner"]
    },
    "not-allowed": {
        "hotspot": (8, 8),
        "aliases": ["circle"]
    },
    "ns-resize": {
        "hotspot": (4, 11),
        "aliases": ["sb_v_double_arrow"]
    },
    "nwse-resize": {
        "hotspot": (8, 8),
        "aliases": ["bottom_right_corner"]
    },
    "pencil": {
        "hotspot": (1, 1)
    },
    "pointer": {
        "hotspot": (6, 1),
        "aliases": ["hand2"]
    },
    "progress": {
        "hotspot": (1, 1),
        "frames": 18,
        "duration": 50,
        "aliases": ["left_ptr_watch"]
    },
    "wait": {
        "hotspot": (16, 16),
        "frames": 18,
        "duration": 50,
        "aliases": ["watch"]
    }
}

sizes = [32]
png_dir = './pngs'
output_dir = '../../Windows 7/cursors/'

def generate_in_file_content(cursor_name, cursor_info):
    in_content = []
    is_animated = "frames" in cursor_info

    frame_range = range(1, cursor_info["frames"] + 1) if is_animated else [1]
    hotspot = cursor_info["hotspot"]

    for frame in frame_range:
        for size in sizes:
            file_name = f"{cursor_name}_{frame:02d}.png" if is_animated else f"{cursor_name}.png"
            png_file_relative = f"pngs/{size}x{size}/{file_name}"
            png_file = os.path.join(png_dir, f"{size}x{size}", file_name)

            hotspot_x = math.floor(hotspot[0] * size / nominal_size)
            hotspot_y = math.floor(hotspot[1] * size / nominal_size)

            entry = f"{size} {hotspot_x} {hotspot_y} {png_file_relative}"
            if is_animated:
                entry += f" {cursor_info['duration']}"
            in_content.append(entry + "\n")

    return ''.join(in_content)

def generate_cursors():
    for cursor_name, cursor_info in cursors.items():
        logging.info(f"Processing cursor: {cursor_name}")


        in_file_content = generate_in_file_content(cursor_name, cursor_info)
        in_file_path = os.path.join(png_dir, f'{cursor_name}.in')

        # Write the .in file in ./pngs/ directory
        try:
            with open(in_file_path, 'w') as in_file:
                in_file.write(in_file_content)
            logging.info(f"Generated .in file: {in_file_path}")
        except Exception as e:
            logging.error(f"Error writing .in file: {in_file_path} - {str(e)}")
            continue

        cursor_output = os.path.join(output_dir, cursor_name) 
        command = ['xcursorgen', in_file_path, cursor_output]
        logging.debug(f"Running command: {' '.join(command)}")
        try:
            subprocess.run(command, check=True)
            logging.info(f"Generated cursor: {cursor_output}")
        except subprocess.CalledProcessError as exception:
            logging.error(f"xcursorgen failed for {cursor_name}: {str(exception)}")

def generate_symlinks():
    for cursor_name, cursor_info in cursors.items():
        for alias in cursor_info.get("aliases", []):
            os.symlink(os.path.join(output_dir, cursor_name), os.path.join(output_dir, alias))

if __name__ == "__main__":
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        logging.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    # Call the main function to generate cursors
    generate_cursors()
    generate_symlinks()
