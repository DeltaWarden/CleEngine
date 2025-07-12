from physics import PhysicsEngine
from renderer import RenderEngine
from sceneSet import SceneRenderer, SceneObject
from cle_lang import CleParser
from hotkeys import HotkeyManager
import time
from tkinter import filedialog, Tk
physics = PhysicsEngine()
renderer = None
cle_parser = CleParser()
scene_renderer = SceneRenderer()
hotkeys = HotkeyManager()
physics_enabled = True
scene_file_path = None
def toggle_physics():
    global physics_enabled
    physics_enabled = not physics_enabled
    scene_renderer.physics_enabled = physics_enabled
    print(f"Physics enabled: {physics_enabled}")
def load_scene():
    global scene_file_path
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CLE files", "*.cle")])
    root.destroy()
    if not file_path:
        print("No file selected")
        return
    print(f"Loading scene from {file_path}")
    scene_file_path = file_path
    scene_renderer.scene_name = file_path.split('/')[-1].split('\\')[-1]
    cle_parser.parse_file(file_path)
    physics.objects.clear()
    scene_renderer.objects.clear()
    for o in cle_parser.get_objects().values():
        if isinstance(o, (tuple, list)):
            obj = SceneObject(o[0], o[1], o[2], o[3])
        else:
            obj = SceneObject(o.name, o.type, o.position, o.scale, o.color, o.texture, o.material, o.emissive)
        physics.add_object(obj)
        scene_renderer.objects.append(obj)
def reload_scene():
    global scene_file_path
    if not scene_file_path:
        print("No scene loaded to reload")
        return
    print(f"Reloading scene from {scene_file_path}")
    scene_renderer.scene_name = scene_file_path.split('/')[-1].split('\\')[-1]
    cle_parser.parse_file(scene_file_path)
    physics.objects.clear()
    scene_renderer.objects.clear()
    for o in cle_parser.get_objects().values():
        if isinstance(o, (tuple, list)):
            obj = SceneObject(o[0], o[1], o[2], o[3])
        else:
            obj = SceneObject(o.name, o.type, o.position, o.scale, o.color, o.texture, o.material, o.emissive)
        physics.add_object(obj)
        scene_renderer.objects.append(obj)
def reset_scene():
    global physics
    for obj in scene_renderer.objects:
        if hasattr(obj, 'position') and hasattr(obj, 'scale'):
            obj.position = (0, 0, 0)
            obj.velocity = (0, 0, 0)
    print("Scene reset: all objects moved to (0,0,0)")
def focus_first_object():
    if scene_renderer.objects:
        obj = scene_renderer.objects[0]
        if hasattr(obj, 'position'):
            x, y, z = obj.position
            renderer.camera_pos_x = x
            renderer.camera_pos_y = y
            renderer.camera_pos_z = z
            print(f"Camera focused on: {obj.name} at {obj.position}")
    else:
        print("No objects to focus on")

def toggle_lighting():
    renderer.use_lighting = not renderer.use_lighting
    print(f"Lighting: {'ON' if renderer.use_lighting else 'OFF'}")

def toggle_wireframe():
    renderer.wireframe_mode = not renderer.wireframe_mode
    print(f"Wireframe: {'ON' if renderer.wireframe_mode else 'OFF'}")

def toggle_ortho():
    renderer.ortho_mode = not renderer.ortho_mode
    renderer.set_projection()
    print(f"Ortho: {'ON' if renderer.ortho_mode else 'OFF'}")

def toggle_textures():
    renderer.use_textures = not renderer.use_textures
    print(f"Textures: {'ON' if renderer.use_textures else 'OFF'}")

def main():
    global renderer
    renderer = RenderEngine(scene_renderer, hotkeys=hotkeys)
    renderer.init_window()
    scene_renderer.buttons_clear()
    scene_renderer.add_button("Toggle Physics", "toggle.png", toggle_physics)
    scene_renderer.add_button("Load Scene", "load.png", load_scene)
    hotkeys.register('r', reset_scene)
    hotkeys.register('f', focus_first_object)
    hotkeys.register('l', reload_scene)
    hotkeys.register('p', toggle_physics)
    hotkeys.register('L', toggle_lighting)
    hotkeys.register('w', toggle_wireframe)
    hotkeys.register('o', toggle_ortho)
    hotkeys.register('t', toggle_textures)
    last_time = time.time()
    while not renderer.should_close():
        now = time.time()
        dt = now - last_time
        last_time = now
        if physics_enabled:
            physics.update(dt)
        renderer.render_frame()
        renderer.poll_events()
    renderer.terminate()
if __name__ == "__main__":
    main()
