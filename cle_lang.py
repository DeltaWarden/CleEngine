from sceneSet import SceneObject
import math

class CleParser:
    def __init__(self):
        self.objects = {}

    def parse_file(self, filepath):
        with open(filepath, 'r') as f:
            for line in f:
                self.parse_line(line)

    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith("#"):
            return
        parts = line.split()
        if parts[0].upper() == "CREATE":
            self.parse_create_command(parts[1:])

    def parse_create_command(self, parts):
        if len(parts) < 8:
            return
        
        name = parts[0]
        obj_type = parts[2]
        pos = tuple(map(float, parts[4:7]))
        scale = tuple(map(float, parts[8:11]))
        
        color = (1.0, 1.0, 1.0)
        texture = None
        material = "default"
        emissive = 0.0
        
        i = 11
        while i < len(parts):
            if parts[i].upper() == "COLOR" and i + 3 < len(parts):
                color = tuple(map(float, parts[i+1:i+4]))
                i += 4
            elif parts[i].upper() == "TEXTURE" and i + 1 < len(parts):
                texture = parts[i+1]
                i += 2
            elif parts[i].upper() == "MATERIAL" and i + 1 < len(parts):
                material = parts[i+1]
                i += 2
            elif parts[i].upper() == "EMISSIVE" and i + 1 < len(parts):
                emissive = float(parts[i+1])
                i += 2
            else:
                i += 1
        
        obj = SceneObject(name, obj_type, pos, scale, color, texture, material, emissive)
        self.objects[name] = obj

    def get_objects(self):
        return self.objects
