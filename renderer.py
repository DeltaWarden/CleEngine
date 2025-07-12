from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

class RenderEngine:
    def __init__(self, scene_renderer, width=800, height=600, hotkeys=None):
        self.scene_renderer = scene_renderer
        self.width = width
        self.height = height
        self.window = None
        self.should_close_flag = False
        self.initialized = False
        self.hotkeys = hotkeys
        self.camera_distance = 2000.0
        self.camera_rot_x = 0.0
        self.camera_rot_y = 0.0
        self.camera_pos_x = 0.0
        self.camera_pos_y = 0.0
        self.camera_pos_z = 0.0
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dragging = False
        self.middle_mouse_dragging = False
        self.fps_counter = 0
        self.fps_time = time.time()
        self.current_fps = 0
        self.use_lighting = False
        self.wireframe_mode = False
        self.ortho_mode = False
        self.use_textures = True

    def init_window(self):
        try:
            glutInit()
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(self.width, self.height)
            self.window = glutCreateWindow(b"CleEngine")
            glClearColor(0.1, 0.1, 0.1, 1.0)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_COLOR_MATERIAL)
            glEnable(GL_NORMALIZE)
            self.setup_lighting()
            self.set_projection()
            glMatrixMode(GL_MODELVIEW)
            glutDisplayFunc(self.display)
            glutIdleFunc(self.display)
            glutReshapeFunc(self.reshape)
            glutMouseFunc(self.mouse_click)
            glutMotionFunc(self.mouse_motion)
            glutPassiveMotionFunc(self.mouse_motion)
            glutKeyboardFunc(self.keyboard_down)
            glutKeyboardUpFunc(self.keyboard_up)
            self.initialized = True
        except Exception as e:
            print(f"Error initializing OpenGL: {e}")
            self.should_close_flag = True

    def set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width / self.height if self.height != 0 else 1
        if self.ortho_mode:
            view_size = 1000
            glOrtho(-view_size * aspect, view_size * aspect, -view_size, view_size, -10000, 10000)
        else:
            gluPerspective(45, aspect, 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)

    def setup_lighting(self):
        if self.use_lighting:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, (1, 1, 2, 0))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
            glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
        else:
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)

    def display(self):
        if not self.initialized:
            return
        try:
            glViewport(0, 0, self.width, self.height)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslatef(-self.camera_pos_x, -self.camera_pos_y, -self.camera_distance - self.camera_pos_z)
            glRotatef(self.camera_rot_x, 1, 0, 0)
            glRotatef(self.camera_rot_y, 0, 1, 0)
            self.setup_lighting()
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if self.wireframe_mode else GL_FILL)
            self.scene_renderer.draw_scene(window_width=self.width, window_height=self.height)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glDisable(GL_LIGHTING)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, self.width, 0, self.height)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            self.scene_renderer.draw_buttons(self.width, self.height)
            self.draw_debug_info()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glutSwapBuffers()
        except Exception as e:
            print(f"Error in display: {e}")
            self.should_close_flag = True

    def draw_debug_info(self):
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(10, self.height - 20)
        glutBitmapString(GLUT_BITMAP_9_BY_15, f"FPS: {self.current_fps}".encode())
        glRasterPos2f(10, self.height - 40)
        glutBitmapString(GLUT_BITMAP_9_BY_15, f"OBJECTS: {len(self.scene_renderer.objects)}".encode())
        glRasterPos2f(10, self.height - 60)
        glutBitmapString(GLUT_BITMAP_9_BY_15, f"SCENE: {self.scene_renderer.scene_name if hasattr(self.scene_renderer, 'scene_name') else 'None'}".encode())
        glRasterPos2f(10, self.height - 80)
        glutBitmapString(GLUT_BITMAP_9_BY_15, f"XYZ CAMERA: {self.camera_pos_x:.1f}, {self.camera_pos_y:.1f}, {self.camera_pos_z:.1f}".encode())
        glRasterPos2f(10, self.height - 100)
        physics_status = "ON" if hasattr(self.scene_renderer, 'physics_enabled') and self.scene_renderer.physics_enabled else "OFF"
        glutBitmapString(GLUT_BITMAP_9_BY_15, f"PHYSICS: {physics_status}".encode())

    def reshape(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self.set_projection()

    def mouse_click(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                py = self.height - y
                if self.scene_renderer.handle_click(x, py):
                    return
                self.mouse_dragging = True
                self.mouse_x = x
                self.mouse_y = y
            else:
                self.mouse_dragging = False
        elif button == GLUT_MIDDLE_BUTTON:
            if state == GLUT_DOWN:
                self.middle_mouse_dragging = True
                self.mouse_x = x
                self.mouse_y = y
            else:
                self.middle_mouse_dragging = False

    def mouse_motion(self, x, y):
        if self.mouse_dragging:
            dx = x - self.mouse_x
            dy = y - self.mouse_y
            self.camera_rot_y += dx * 0.5
            self.camera_rot_x += dy * 0.5
            self.camera_rot_x = max(-90, min(90, self.camera_rot_x))
            self.mouse_x = x
            self.mouse_y = y
        elif self.middle_mouse_dragging:
            dx = x - self.mouse_x
            dy = y - self.mouse_y
            self.camera_pos_x += dx * 5.0
            self.camera_pos_y += dy * 5.0
            self.mouse_x = x
            self.mouse_y = y

    def keyboard_down(self, key, x, y):
        if self.hotkeys:
            try:
                self.hotkeys.handle(key.decode())
            except Exception:
                pass

    def keyboard_up(self, key, x, y):
        pass

    def update_camera_movement(self):
        pass

    def update_fps(self):
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_time = current_time

    def render_frame(self):
        self.update_camera_movement()
        self.update_fps()
        glutPostRedisplay()

    def poll_events(self):
        glutMainLoopEvent()

    def should_close(self):
        return self.should_close_flag

    def terminate(self):
        self.scene_renderer.close()
