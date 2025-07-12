import zipfile
import io
from PIL import Image
from OpenGL.GL import *
import math

class SceneObject:
    def __init__(self, name, obj_type, position, scale, color=(1.0, 1.0, 1.0), texture=None, material="default", emissive=0.0):
        self.name = name
        self.type = obj_type
        self.position = position
        self.scale = scale
        self.color = color
        self.texture = texture
        self.material = material
        self.emissive = emissive
        self.velocity = (0.0, 0.0, 0.0)
        self.texture_id = None

    def draw(self, renderer=None):
        x, y, z = self.position
        size = max(self.scale) * 100
        
        glColor3f(*self.color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(size, size, size)
        
        if self.type.lower() == "cube":
            self.draw_cube()
        elif self.type.lower() == "sphere":
            self.draw_sphere()
        elif self.type.lower() == "plane":
            self.draw_plane()
        elif self.type.lower() == "cylinder":
            self.draw_cylinder()
        elif self.type.lower() == "light":
            self.draw_light()
        else:
            self.draw_cube()
        
        glPopMatrix()

    def draw_cube(self):
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        glNormal3f(0, 0, -1)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        glNormal3f(0, -1, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        glNormal3f(1, 0, 0)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glEnd()

    def draw_sphere(self):
        slices = 16
        stacks = 16
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0 * 0.5, y * zr0 * 0.5, z0 * 0.5)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1 * 0.5, y * zr1 * 0.5, z1 * 0.5)
            glEnd()

    def draw_plane(self):
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0, -0.5)
        glVertex3f(0.5, 0, -0.5)
        glVertex3f(0.5, 0, 0.5)
        glVertex3f(-0.5, 0, 0.5)
        glEnd()

    def draw_cylinder(self):
        slices = 16
        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle) * 0.5
            z = math.sin(angle) * 0.5
            glNormal3f(x, 0, z)
            glVertex3f(x, -0.5, z)
            glVertex3f(x, 0.5, z)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(0, 0.5, 0)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle) * 0.5
            z = math.sin(angle) * 0.5
            glVertex3f(x, 0.5, z)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, -1, 0)
        glVertex3f(0, -0.5, 0)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle) * 0.5
            z = math.sin(angle) * 0.5
            glVertex3f(x, -0.5, z)
        glEnd()

    def draw_light(self):
        if self.emissive > 0:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(*self.color, self.emissive)
        self.draw_sphere()
        if self.emissive > 0:
            glDisable(GL_BLEND)
            glColor3f(*self.color)

class Button:
    def __init__(self, x, y, width, height, label, image_data, callback=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.callback = callback
        self.texture_id = self._load_texture(image_data) if image_data else None

    def _load_texture(self, image_data):
        try:
            image = Image.open(io.BytesIO(image_data)).convert("RGBA")
            ix, iy = image.size
            image_data = image.tobytes("raw", "RGBA", 0, -1)
            tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            return tex_id
        except Exception as e:
            print(f"Warning: Failed to load texture: {e}")
            return None

    def draw(self, renderer=None):
        button_size = min(self.width, self.height)
        x = self.x
        y = self.y
        use_textures = True
        if renderer and hasattr(renderer, 'use_textures'):
            use_textures = renderer.use_textures
        if self.texture_id is None or not use_textures:
            glColor3f(0.2, 0.2, 0.2)
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + button_size, y)
            glVertex2f(x + button_size, y + button_size)
            glVertex2f(x, y + button_size)
            glEnd()
        else:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1)
            glVertex2f(x, y)
            glTexCoord2f(1, 1)
            glVertex2f(x + button_size, y)
            glTexCoord2f(1, 0)
            glVertex2f(x + button_size, y + button_size)
            glTexCoord2f(0, 0)
            glVertex2f(x, y + button_size)
            glEnd()
            glDisable(GL_TEXTURE_2D)

    def contains(self, px, py):
        button_size = min(self.width, self.height)
        return (self.x <= px <= self.x + button_size and 
                self.y <= py <= self.y + button_size)

class SceneRenderer:
    def __init__(self):
        self.objects = []
        self.buttons = []
        self.assets = zipfile.ZipFile("assets.pack", "r")
        self.scene_name = "None"
        self.physics_enabled = False

    def buttons_clear(self):
        self.buttons.clear()

    def add_button(self, label, image_name, callback=None):
        btn = Button(0, 0, 0, 0, label, None, callback)
        try:
            image_data = self.assets.read(image_name)
            print(f"Successfully loaded texture: {image_name} ({len(image_data)} bytes)")
            btn.texture_id = btn._load_texture(image_data)
        except KeyError:
            print(f"Warning: {image_name} not found in assets.pack")
        except Exception as e:
            print(f"Error loading {image_name}: {e}")
        self.buttons.append(btn)

    def draw_scene(self, window_width=None, window_height=None):
        for obj in self.objects:
            obj.draw(renderer=getattr(self, 'renderer', None))

    def draw_buttons(self, window_width, window_height):
        btn_size = int(min(window_width, window_height) * 0.12)
        margin = int(btn_size * 0.1)
        for i, btn in enumerate(self.buttons):
            btn.x = margin + i * (btn_size + margin)
            btn.y = margin
            btn.width = btn_size
            btn.height = btn_size
            btn.draw()

    def handle_click(self, x, y):
        for btn in self.buttons:
            if btn.contains(x, y) and btn.callback:
                btn.callback()
                return True
        return False

    def close(self):
        self.assets.close()
