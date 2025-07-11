import glfw
from OpenGL.GL import *
from PIL import Image
import numpy as np
import zipfile
from io import BytesIO
import os
import tkinter as tk
from tkinter import filedialog
from cle_lang import CleParser

BUTTON_COUNT = 7
BUTTON_PADDING = 8
BUTTON_BOTTOM_OFFSET = 20

MAX_BUTTON_WIDTH = 100
MAX_BUTTON_HEIGHT = 60

BUTTON_IMAGE_NAMES = [
    "PlayButton.png",
    "PauseButton.png",
    "StopButton.png",
    "LoadButton.png",
    "UnloadButton.png",
    "BookButton.png",
    "DebugButton.png",
]

ARCHIVE_PATH = "assets.pack"


class Button:
    def __init__(self, image_data, image_name):
        self.image_name = image_name
        self.texture = None
        self.width = 0
        self.height = 0

        self.img = Image.open(BytesIO(image_data)).convert("RGBA")
        self.img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        self.load_texture()

    def load_texture(self):
        w, h = self.img.size
        scale = min(MAX_BUTTON_WIDTH / w, MAX_BUTTON_HEIGHT / h, 1)
        self.width = int(w * scale)
        self.height = int(h * scale)

        if scale != 1:
            img_resized = self.img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        else:
            img_resized = self.img

        img_data = np.array(img_resized).astype(np.uint8)

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    def draw(self, x, y):
        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + self.width, y)
        glVertex2f(x + self.width, y + self.height)
        glVertex2f(x, y + self.height)
        glEnd()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(x, y)
        glTexCoord2f(1, 0)
        glVertex2f(x + self.width, y)
        glTexCoord2f(1, 1)
        glVertex2f(x + self.width, y + self.height)
        glTexCoord2f(0, 1)
        glVertex2f(x, y + self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)


class RenderableObject:
    def __init__(self, name, obj_type, position, scale):
        self.name = name
        self.type = obj_type
        self.position = position
        self.scale = scale

    def draw(self):
        x, y, z = self.position
        sx, sy, sz = self.scale

        size = max(sx, sy) * 30

        if self.type.lower() == "cube":
            color = (0.0, 0.5, 1.0)
        elif self.type.lower() == "sphere":
            color = (1.0, 0.5, 0.0)
        else:
            color = (0.7, 0.7, 0.7)
        draw_x = 50 + x * 50
        draw_y = 150 + y * 50

        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(draw_x, draw_y)
        glVertex2f(draw_x + size, draw_y)
        glVertex2f(draw_x + size, draw_y + size)
        glVertex2f(draw_x, draw_y + size)
        glEnd()

buttons = []
scene_objects = []
cle_parser = CleParser()

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CLE files", "*.cle")])
    root.destroy()
    return file_path


def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        xpos, ypos = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        ypos = height - ypos

        x = BUTTON_PADDING
        btn_top = height - MAX_BUTTON_HEIGHT - BUTTON_BOTTOM_OFFSET
        for i, btn in enumerate(buttons):
            if x <= xpos <= x + btn.width and btn_top <= ypos <= btn_top + btn.height:
                print(f"[🖱] Нажата кнопка #{i + 1} (файл: {btn.image_name})")
                if i == 3:
                    path = open_file_dialog()
                    if path and os.path.isfile(path):
                        load_scene_from_cle(path)
                break
            x += btn.width + BUTTON_PADDING

def load_scene_from_cle(path):
    global scene_objects, cle_parser
    print(f"Загружаю сцену из: {path}")
    cle_parser.parse_file(path)
    scene_objects = []
    for name, obj in cle_parser.get_objects().items():
        ro = RenderableObject(name, obj.type, obj.position, obj.scale)
        scene_objects.append(ro)
    print(f"Загружено объектов: {len(scene_objects)}")

def draw_scene():
    glDisable(GL_TEXTURE_2D)
    for obj in scene_objects:
        obj.draw()
    glEnable(GL_TEXTURE_2D)

def draw_buttons(width, height):
    x = BUTTON_PADDING
    y = height - MAX_BUTTON_HEIGHT - BUTTON_BOTTOM_OFFSET
    for btn in buttons:
        btn.draw(x, y)
        x += btn.width + BUTTON_PADDING

def main():
    global buttons

    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Кнопки + сцена из CLE", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    buttons = []
    try:
        with zipfile.ZipFile(ARCHIVE_PATH, 'r') as archive:
            for img_name in BUTTON_IMAGE_NAMES:
                try:
                    image_data = archive.read(img_name)
                    btn = Button(image_data, img_name)
                    buttons.append(btn)
                except KeyError:
                    print(f"В архиве нет файла: {img_name}")
    except Exception as e:
        print(f"Ошибка открытия архива {ARCHIVE_PATH}: {e}")

    while not glfw.window_should_close(window):
        width, height = glfw.get_window_size(window)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        draw_scene()
        draw_buttons(width, height)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
