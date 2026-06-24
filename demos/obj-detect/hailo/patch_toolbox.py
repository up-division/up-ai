#!/usr/bin/env python3
from pathlib import Path

def patch_toolbox_file():
    # 1. Automatically find the path to toolbox.py in the project
    toolbox_path = None
    for p in Path(__file__).resolve().parents:
        potential_path = p / "hailo_10h" / "hailo_apps" / "python" / "core" / "common" / "toolbox.py"
        if potential_path.exists():
            toolbox_path = potential_path
            break
    
    if not toolbox_path:
        print("❌ The toolbox.py file could not be found. Please check that this script is placed in the correct project directory.")
        return

    print(f"🔍 Target file found: {toolbox_path}")

    # 2. Read the original file content
    with open(toolbox_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. Define the original code block (old logic).
    old_code = """                    # Allow quitting with 'q'
                    if (cv2.waitKey(1) & 0xFF) == ord("q"):
                        if stop_event is not None:
                            stop_event.set()
                        continue"""

    # 4. Define the modified code block (new logic).
    new_code = """                    # Allow quitting with 'q' or closing window
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q") or cv2.getWindowProperty("Output", cv2.WND_PROP_VISIBLE) < 1:
                        if stop_event is not None:
                            stop_event.set()
                        break"""

    # 5. Perform replacement and write back the file
    if old_code in content:
        updated_content = content.replace(old_code, new_code)
        with open(toolbox_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("✅ Successfully implemented the window closing mechanism in toolbox.py!")
    elif new_code in content:
        print("ℹ️ toolbox.py was already a modified version!")
    else:
        print("⚠️ Unable to accurately match legacy code!")

if __name__ == "__main__":
    patch_toolbox_file()