# simulation.py
import math

class Simulation:

    def __init__(self, planes, scene, cx, cy, R, collision_dist=18.0):
        self.planes = planes
        self.scene = scene
        self.cx = cx
        self.cy = cy
        self.R = R
        self.collision_dist = collision_dist

    def update_positions(self, dt):
        for plane in self.planes:
            st = plane.state
            rad = math.radians(st.heading_deg)

            nx = st.x + st.speed * math.cos(rad) * dt
            ny = st.y + st.speed * math.sin(rad) * dt

            dx, dy = nx - self.cx, ny - self.cy
            dist = math.hypot(dx, dy)

            if dist >= self.R:
                nx_norm = dx/dist if dist else 1
                ny_norm = dy/dist if dist else 0

                vx = math.cos(rad)
                vy = math.sin(rad)
                dot = vx*nx_norm + vy*ny_norm

                rvx = vx - 2*dot*nx_norm
                rvy = vy - 2*dot*ny_norm

                st.heading_deg = math.degrees(math.atan2(rvy, rvx)) % 360
                nx = self.cx + (self.R - 1)*nx_norm
                ny = self.cy + (self.R - 1)*ny_norm

            st.x, st.y = nx, ny
            b = plane.boundingRect()
            plane.setPos(nx - b.width()/2, ny - b.height()/2)
            plane.setRotation(st.heading_deg)

    def collisions(self):
        to_remove = set()
        for i in range(len(self.planes)):
            for j in range(i+1, len(self.planes)):
                a = self.planes[i].state
                b = self.planes[j].state
                if a.altitude != b.altitude:
                    continue
                d = math.hypot(a.x - b.x, a.y - b.y)
                if d < self.collision_dist:
                    to_remove.add(i)
                    to_remove.add(j)
        return sorted(to_remove, reverse=True)
