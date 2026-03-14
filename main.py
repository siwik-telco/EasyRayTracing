import tkinter as tk
from tkinter import ttk
import math
from models import Antenna, Ray
from physics import PhysicsEngine
from scenarios import ScenarioBuilder

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("RF Raytracing Simulator")
        self.physics = PhysicsEngine()
        self.scenarios = ScenarioBuilder()

        self.canvas_width = 800
        self.canvas_height = 600

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(root, width=220, padx=10, pady=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.freq_var = tk.IntVar(value=800)
        self.freq_combo = ttk.Combobox(self.control_frame, textvariable=self.freq_var, state="readonly")
        self.freq_combo['values'] = (800, 900, 2100, 2600, 3600, 7000, 15000, 24000)
        self.freq_combo.pack(pady=5)

        self.scenario_var = tk.StringVar(value="Single")
        self.scenario_combo = ttk.Combobox(self.control_frame, textvariable=self.scenario_var, state="readonly")
        self.scenario_combo['values'] = ("Single", "Double", "Block", "Corridor")
        self.scenario_combo.pack(pady=5)

        self.antenna_var = tk.StringVar(value="Omnidirectional")
        self.antenna_combo = ttk.Combobox(self.control_frame, textvariable=self.antenna_var, state="readonly")
        self.antenna_combo['values'] = ("Omnidirectional", "Directional")
        self.antenna_combo.pack(pady=5)

        self.view_var = tk.StringVar(value="Rays")
        self.view_label = tk.Label(self.control_frame, text="View mode:")
        self.view_label.pack(pady=(15, 0))
        self.view_combo = ttk.Combobox(self.control_frame, textvariable=self.view_var, state="readonly")
        self.view_combo['values'] = ("Rays", "Heatmap top-down")
        self.view_combo.pack(pady=5)

        self.rsrp_label = tk.Label(self.control_frame, text="RSRP: 0 dBm", font=("Arial", 12, "bold"))
        self.rsrp_label.pack(pady=20)

        self.status_label = tk.Label(self.control_frame, text="", font=("Arial", 9))
        self.status_label.pack(pady=5)

        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.freq_combo.bind("<<ComboboxSelected>>", self.rebuild_environment)
        self.scenario_combo.bind("<<ComboboxSelected>>", self.rebuild_environment)
        self.antenna_combo.bind("<<ComboboxSelected>>", self.rebuild_environment)
        self.view_combo.bind("<<ComboboxSelected>>", self.rebuild_environment)

        self.mouse_x = 0
        self.mouse_y = 0

        self.heatmap_grid = []
        self.heatmap_min = -140
        self.heatmap_max = -40

        self.legend_steps = [-120, -110, -100, -90, -80, -70]

        self.rebuild_environment()
    def draw_legend(self):
        x0 = 10
        y0 = 350
        width = 20
        height = 200
        segments = 40
        segment_h = height / segments

        for i in range(segments):
            v = 1.0 - i / (segments - 1)
            rsrp = self.heatmap_min + v * (self.heatmap_max - self.heatmap_min)
            color = self.rsrp_to_heat_color(rsrp)
            sy0 = y0 + i * segment_h
            sy1 = sy0 + segment_h + 1
            self.canvas.create_rectangle(x0, sy0, x0 + width, sy1, outline="", fill=color, tags="static")

        self.canvas.create_rectangle(x0, y0, x0 + width, y0 + height, outline="white", width=1, tags="static")

        for val in self.legend_steps:
            if val < self.heatmap_min or val > self.heatmap_max:
                continue
            v = (val - self.heatmap_min) / (self.heatmap_max - self.heatmap_min)
            ly = y0 + (1.0 - v) * height
            self.canvas.create_line(x0 + width, ly, x0 + width + 5, ly, fill="white", tags="static")
            self.canvas.create_text(x0 + width + 40, ly, text=f"{int(val)} dBm", anchor="w", fill="white", font=("Arial", 8), tags="static")

        self.canvas.create_text(x0 + width / 2, y0 - 10, text="RSRP", fill="white", font=("Arial", 9, "bold"), tags="static")

    def get_buildings(self):
        val = self.scenario_var.get()
        if val == "Single":
            return self.scenarios.get_single_building()
        if val == "Double":
            return self.scenarios.get_two_buildings()
        if val == "Block":
            return self.scenarios.get_block()
        return self.scenarios.get_corridor()

    def calculate_color(self, rsrp):
        if rsrp > -70:
            return "#00FF00"
        if rsrp > -90:
            return "#FFFF00"
        if rsrp > -105:
            return "#FF8800"
        if rsrp > -120:
            return "#FF0000"
        return "#333333"

    def rsrp_to_heat_color(self, rsrp):
        if rsrp < self.heatmap_min:
            v = 0.0
        elif rsrp > self.heatmap_max:
            v = 1.0
        else:
            v = (rsrp - self.heatmap_min) / (self.heatmap_max - self.heatmap_min)

        if v < 0.2:
            t = v / 0.2
            r = int(0 + t * (75 - 0))
            g = int(0 + t * (0 - 0))
            b = int(130 + t * (130 - 130))
        elif v < 0.4:
            t = (v - 0.2) / 0.2
            r = int(75 + t * (128 - 75))
            g = int(0 + t * (0 - 0))
            b = int(130 + t * (128 - 130))
        elif v < 0.6:
            t = (v - 0.4) / 0.2
            r = int(128 + t * (220 - 128))
            g = int(0 + t * (50 - 0))
            b = int(128 + t * (0 - 128))
        elif v < 0.8:
            t = (v - 0.6) / 0.2
            r = int(220 + t * (255 - 220))
            g = int(50 + t * (165 - 50))
            b = 0
        else:
            t = (v - 0.8) / 0.2
            r = int(255 + t * (0 - 255))
            g = int(165 + t * (255 - 165))
            b = 0

        return f"#{r:02X}{g:02X}{b:02X}"

    def rebuild_environment(self, event=None):
        self.canvas.delete("all")
        self.buildings = self.get_buildings()

        freq = self.freq_var.get()
        is_dir = self.antenna_var.get() == "Directional"
        self.antenna = Antenna(100, 300, 40, freq, is_dir)

        view = self.view_var.get()
        if view == "Rays":
            self.build_ray_view()
        else:
            self.build_heatmap_view()
            self.draw_legend()
            self.status_label.config(text="View: top-down heatmap")

        self.update_cursor()

    def build_ray_view(self):
        for b in self.buildings:
            self.canvas.create_rectangle(b.x, b.y, b.x + b.width, b.y + b.height, outline="#00FFFF", fill="#112233", tags="static")

        self.canvas.create_oval(self.antenna.x-5, self.antenna.y-5, self.antenna.x+5, self.antenna.y+5, fill="white", tags="static")

        for angle in self.antenna.get_angles():
            ray = Ray(self.antenna.x, self.antenna.y, angle)
            self.trace_ray(ray.start_x, ray.start_y, ray.dx, ray.dy, 0, 0, 0, 0, 1)

        self.status_label.config(text="View: rays with reflections")

    def build_heatmap_view(self):
        for b in self.buildings:
            self.canvas.create_rectangle(b.x, b.y, b.x + b.width, b.y + b.height, outline="#00FFFF", fill="#112233", tags="static")

        self.canvas.create_oval(self.antenna.x-5, self.antenna.y-5, self.antenna.x+5, self.antenna.y+5, fill="white", tags="static")

        cell_size = 10
        cols = self.canvas_width // cell_size
        rows = self.canvas_height // cell_size
        self.heatmap_grid = [[-140 for _ in range(cols)] for _ in range(rows)]

        freq = self.freq_var.get()
        tx = self.antenna.tx_power

        for row in range(rows):
            for col in range(cols):
                cx = col * cell_size + cell_size / 2
                cy = row * cell_size + cell_size / 2
                dist = math.hypot(cx - self.antenna.x, cy - self.antenna.y)
                if dist == 0:
                    rsrp = tx
                else:
                    walls = 0
                    steps = max(1, int(dist))
                    prev_in_b = False
                    for s in range(steps):
                        px = self.antenna.x + (cx - self.antenna.x) * (s / steps)
                        py = self.antenna.y + (cy - self.antenna.y) * (s / steps)
                        in_b = any(b.intersects(px, py) for b in self.buildings)
                        if in_b and not prev_in_b:
                            walls += 1
                        prev_in_b = in_b
                    rsrp = self.physics.calculate_rsrp(tx, dist, freq, walls, 0)
                self.heatmap_grid[row][col] = rsrp

        for row in range(rows):
            for col in range(cols):
                rsrp = self.heatmap_grid[row][col]
                color = self.rsrp_to_heat_color(rsrp)
                x0 = col * cell_size
                y0 = row * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="", fill=color, tags="static")

        self.status_label.config(text="View: top-down heatmap")

    def trace_ray(self, start_x, start_y, dx, dy, init_dist, walls, bounces, extra_loss, max_bounces):
        freq = self.freq_var.get()
        max_dist = 800
        step_size = 10

        x, y = start_x, start_y
        prev_in_b = any(b.intersects(x, y) for b in self.buildings)

        for step in range(0, max_dist - init_dist, step_size):
            nx = x + dx * step_size
            ny = y + dy * step_size
            dist = init_dist + step + step_size

            in_b = False
            hit_b = None
            for b in self.buildings:
                if b.intersects(nx, ny):
                    in_b = True
                    hit_b = b
                    break

            if in_b and not prev_in_b:
                walls += 1
                if bounces < max_bounces:
                    fx, fy = hit_b.get_reflection_multipliers(x, y, nx, ny)
                    rx, ry = dx * fx, dy * fy
                    refl_loss = extra_loss + self.physics.get_reflection_loss(freq)
                    self.trace_ray(x, y, rx, ry, dist, walls - 1, bounces + 1, refl_loss, max_bounces)

            prev_in_b = in_b

            rsrp = self.physics.calculate_rsrp(self.antenna.tx_power, dist, freq, walls, extra_loss)

            if rsrp > -140:
                color = self.calculate_color(rsrp)
                self.canvas.create_line(x, y, nx, ny, fill=color, tags="static")
            else:
                break

            x, y = nx, ny

    def on_mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.update_cursor()

    def update_cursor(self):
        self.canvas.delete("cursor")

        if not hasattr(self, 'antenna'):
            return

        freq = self.freq_var.get()

        receiver_dist = math.hypot(self.mouse_x - self.antenna.x, self.mouse_y - self.antenna.y)
        walls_to_rx = 0
        steps = max(1, int(receiver_dist))
        prev_in_b = False

        for step in range(steps):
            check_x = self.antenna.x + (self.mouse_x - self.antenna.x) * (step / steps)
            check_y = self.antenna.y + (self.mouse_y - self.antenna.y) * (step / steps)
            in_b = any(b.intersects(check_x, check_y) for b in self.buildings)
            if in_b and not prev_in_b:
                walls_to_rx += 1
            prev_in_b = in_b

        rsrp_val = self.physics.calculate_rsrp(self.antenna.tx_power, receiver_dist, freq, walls_to_rx, 0)

        self.rsrp_label.config(text=f"RSRP at Cursor:\n{rsrp_val:.2f} dBm")
        self.canvas.create_oval(self.mouse_x-5, self.mouse_y-5, self.mouse_x+5, self.mouse_y+5, fill="red", tags="cursor")
        self.canvas.create_line(self.antenna.x, self.antenna.y, self.mouse_x, self.mouse_y, fill="white", dash=(4, 4), tags="cursor")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
