import tkinter as tk
from tkinter import colorchooser, ttk
import json
import random

class GridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid with Movable Dots")
        
        self.grid_size = 50  # Increase the grid size
        self.cell_size = 20
        self.canvas_size = self.grid_size * self.cell_size

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.grid(row=0, column=0, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=800, bg='white', scrollregion=(0, 0, self.canvas_size, self.canvas_size))
        self.canvas.grid(row=0, column=0)

        self.hbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky=tk.EW)
        self.vbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        
        self.sidebar = tk.Frame(self.root)
        self.sidebar.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        self.color_picker = tk.Button(self.sidebar, text="Choose Color", command=self.choose_color)
        self.color_picker.pack(pady=10)
        
        self.add_circle_btn = tk.Button(self.sidebar, text="Add Circle", command=self.add_random_circle)
        self.add_circle_btn.pack(pady=10)
        
        self.delete_circle_btn = tk.Button(self.sidebar, text="Delete Circle", command=self.delete_random_circle)
        self.delete_circle_btn.pack(pady=10)
        
        self.color_boxes = tk.Frame(self.sidebar)
        self.color_boxes.pack(pady=10)
        
        self.condition_selector = ttk.Combobox(self.sidebar, state="readonly")
        self.condition_selector.pack(pady=10)
        self.condition_selector.bind("<<ComboboxSelected>>", self.on_condition_selected)

        self.spell_selector = ttk.Combobox(self.sidebar, state="readonly")
        self.spell_selector.pack(pady=10)
        self.spell_selector.bind("<<ComboboxSelected>>", self.on_spell_selected)

        self.deselect_spell_btn = tk.Button(self.sidebar, text="Deselect Spell", command=self.deselect_spell)
        self.deselect_spell_btn.pack(pady=10)

        self.conditions = self.load_conditions()  # Load conditions from JSON file or define them in a dictionary
        self.condition_colors = self.get_condition_colors()  # Define neon colors for each condition
        self.selected_color = "#ff0000"
        self.circles = []
        self.dragging_circle = None
        self.circle_info = {}  # Dictionary to hold name, move speed, and condition for each circle
        self.spells = self.load_spells()  # Load spells from JSON file
        self.selected_condition = None
        self.selected_spell = None

        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_hover)

        self.populate_condition_selector()
        self.populate_spell_selector()

    def draw_grid(self):
        for i in range(0, self.canvas_size, self.cell_size):
            self.canvas.create_line(i, 0, i, self.canvas_size, fill="#ddd")
            self.canvas.create_line(0, i, self.canvas_size, i, fill="#ddd")
    
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Color")
        if color_code:
            self.selected_color = color_code[1]

    def add_random_circle(self):
        x = random.randint(0, self.grid_size - 1)
        y = random.randint(0, self.grid_size - 1)
        self.add_circle(x, y, self.selected_color)
        
    def delete_random_circle(self):
        if self.circles:
            circle = self.circles.pop()
            self.canvas.delete(circle["id"])
            if circle["id"] in self.circle_info:
                del self.circle_info[circle["id"]]
            self.update_color_boxes()

    def add_circle(self, x, y, color):
        center_x = x * self.cell_size + self.cell_size / 2
        center_y = y * self.cell_size + self.cell_size / 2
        radius = self.cell_size / 2.5
        circle_id = self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill=color, outline="#003300", width=2)
        self.circles.append({"id": circle_id, "x": x, "y": y, "color": color})
        self.create_color_box(color)
        self.circle_info[circle_id] = {"name": "", "move_speed": "", "condition": "None"}

    def create_color_box(self, color):
        existing = self.color_boxes.pack_slaves()
        for widget in existing:
            if widget["bg"] == color:
                return
        color_box = tk.Frame(self.color_boxes, bg=color, width=20, height=20)
        color_box.pack(pady=5, fill=tk.X)
        color_box.bind("<Button-1>", lambda e: self.set_selected_color(color))
        
        name_label = tk.Label(color_box, text="Name:")
        name_label.pack(side=tk.LEFT)
        name_entry = tk.Entry(color_box)
        name_entry.pack(side=tk.LEFT)

        move_speed_label = tk.Label(color_box, text="Move Speed:")
        move_speed_label.pack(side=tk.LEFT)
        move_speed_entry = tk.Entry(color_box)
        move_speed_entry.pack(side=tk.LEFT)

        def update_circle_info(event):
            for circle in self.circles:
                if circle["color"] == color:
                    self.circle_info[circle["id"]] = {
                        "name": name_entry.get(),
                        "move_speed": move_speed_entry.get(),
                        "condition": self.circle_info[circle["id"]]["condition"]
                    }

        name_entry.bind("<KeyRelease>", update_circle_info)
        move_speed_entry.bind("<KeyRelease>", update_circle_info)

    def set_selected_color(self, color):
        self.selected_color = color

    def load_conditions(self):
        # Define conditions in a dictionary or load from a JSON file
        conditions = {
            "None": "#000000",
            "Blinded": "#FFFF00",
            "Charmed": "#FF69B4",
            "Deafened": "#00FFFF",
            "Frightened": "#7FFF00",
            "Grappled": "#FFA500",
            "Incapacitated": "#FF4500",
            "Invisible": "#800080",
            "Paralyzed": "#00CED1",
            "Petrified": "#FF00FF",
            "Poisoned": "#32CD32",
            "Prone": "#EE82EE",
            "Restrained": "#ADFF2F",
            "Stunned": "#40E0D0",
            "Unconscious": "#FA8072"
        }
        return conditions

    def get_condition_colors(self):
        return self.conditions

    def load_spells(self):
        # Define example spells for testing
        spells = [
            {"name": "Fireball", "range": 150, "shape": "circle", "radius": 20},
            {"name": "Lightning Bolt", "range": 100, "shape": "line", "length": 100, "width": 5}
        ]
        return spells

    def populate_condition_selector(self):
        condition_names = list(self.conditions.keys())
        self.condition_selector['values'] = condition_names

    def populate_spell_selector(self):
        spell_names = [spell["name"] for spell in self.spells]
        self.spell_selector['values'] = spell_names

    def on_condition_selected(self, event):
        selected_condition_name = self.condition_selector.get()
        self.selected_condition = selected_condition_name

    def on_spell_selected(self, event):
        selected_spell_name = self.spell_selector.get()
        self.selected_spell = next((spell for spell in self.spells if spell["name"] == selected_spell_name), None)

    def deselect_spell(self):
        self.selected_spell = None
        self.spell_selector.set("")
        self.canvas.delete("spell_range")

    def update_color_boxes(self):
        # Clear current color boxes
        for widget in self.color_boxes.winfo_children():
            widget.destroy()
        # Add color boxes for existing colors
        colors = set(circle["color"] for circle in self.circles)
        for color in colors:
            self.create_color_box(color)

    def on_canvas_click(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        circle = self.get_circle_at_position(x, y)
        if circle:
            self.dragging_circle = circle
            self.show_move_range(circle)
            if self.selected_condition:
                self.set_circle_condition(circle, self.selected_condition)
            if self.selected_spell:
                self.show_spell_range(circle)
        else:
            self.add_circle(x, y, self.selected_color)

    def show_move_range(self, circle):
        self.canvas.delete("move_range")
        move_speed = self.circle_info[circle["id"]]["move_speed"]
        if move_speed.isdigit():
            move_distance = int(move_speed) // 5
            x = circle["x"]
            y = circle["y"]
            for dx in range(-move_distance, move_distance + 1):
                for dy in range(-move_distance, move_distance + 1):
                    if abs(dx) + abs(dy) <= move_distance:
                        self.highlight_cell(x + dx, y + dy, "move_range")

    def highlight_cell(self, x, y, tag):
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.canvas.create_rectangle(
                x * self.cell_size,
                y * self.cell_size,
                (x + 1) * self.cell_size,
                (y + 1) * self.cell_size,
                outline="blue" if tag == "move_range" else "red",
                tags=tag
            )

    def set_circle_condition(self, circle, condition):
        color = self.condition_colors.get(condition, "#000000")
        self.canvas.itemconfig(circle["id"], outline=color, width=4)
        self.circle_info[circle["id"]]["condition"] = condition

    def show_spell_range(self, circle):
        self.canvas.delete("spell_range")
        if self.selected_spell:
            x = circle["x"]
            y = circle["y"]
            range_cells = self.selected_spell["range"] // 5
            shape = self.selected_spell["shape"]
            
            if shape == "circle":
                radius_cells = self.selected_spell["radius"] // 5
                for dx in range(-radius_cells, radius_cells + 1):
                    for dy in range(-radius_cells, radius_cells + 1):
                        if dx ** 2 + dy ** 2 <= radius_cells ** 2:
                            self.highlight_cell(x + dx, y + dy, "spell_range")
            elif shape == "line":
                length_cells = self.selected_spell["length"] // 5
                width_cells = self.selected_spell["width"] // 5
                for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    for i in range(-width_cells // 2, width_cells // 2 + 1):
                        for j in range(1, length_cells + 1):
                            self.highlight_cell(x + j * direction[0], y + j * direction[1] + i, "spell_range")
                            self.highlight_cell(x + i, y + j * direction[1], "spell_range")

    def on_canvas_drag(self, event):
        if self.dragging_circle:
            x = event.x // self.cell_size
            y = event.y // self.cell_size
            self.update_circle_position(self.dragging_circle, x, y)

    def on_canvas_release(self, event):
        self.dragging_circle = None
        self.canvas.delete("move_range")

    def on_canvas_hover(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        circle = self.get_circle_at_position(x, y)
        if circle:
            info = self.circle_info[circle["id"]]
            self.canvas.delete("tooltip")
            tooltip_text = f"Name: {info['name']}\nCondition: {info['condition']}"
            if info["name"] or info["condition"]:
                self.canvas.create_text(event.x, event.y - 10, text=tooltip_text, tags="tooltip", fill="black")
        else:
            self.canvas.delete("tooltip")

    def get_circle_at_position(self, x, y):
        for circle in self.circles:
            if circle["x"] == x and circle["y"] == y:
                return circle
        return None

    def update_circle_position(self, circle, x, y):
        center_x = x * self.cell_size + self.cell_size / 2
        center_y = y * self.cell_size + self.cell_size / 2
        radius = self.cell_size / 2.5
        self.canvas.coords(circle["id"], center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        circle["x"] = x
        circle["y"] = y

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()
