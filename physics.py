GRAVITY = -981.0
PHYSICS_STEP = 1 / 120

class PhysicsEngine:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def update(self, dt):
        steps = int(dt // PHYSICS_STEP)
        remainder = dt % PHYSICS_STEP
        for _ in range(steps):
            self._step(PHYSICS_STEP)
        if remainder > 0:
            self._step(remainder)

    def _step(self, dt):
        for obj in self.objects:
            vx, vy, vz = getattr(obj, "velocity", (0, 0, 0))
            x, y, z = obj.position

            vy += GRAVITY * dt
            x += vx * dt
            y += vy * dt
            z += vz * dt

            if y < 0:
                y = 0
                vy = 0

            if x < -5000:
                x = -5000
                vx = 0
            elif x > 5000:
                x = 5000
                vx = 0

            obj.velocity = (vx, vy, vz)
            obj.position = (x, y, z)
