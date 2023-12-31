import numpy as np
import threading
from tkinter import  PhotoImage, Tk, Label, Canvas, Menu, Event, NW
from typing import Any
from game import Game
from functools import partial
from PIL import ImageTk, Image, ImageDraw
import matplotlib.pyplot as plt

def _photo_image(image: np.ndarray):
    image /= np.max(image)
    image *= 255
    image = image.astype(np.uint8)
    revert_image = 255 - image
    filler_image = np.ndarray((*image.shape, 3), dtype=np.uint8)
    for i in range(3):
        filler_image[:, :, i] = revert_image
    
    image = image.astype(np.uint(8))
    pil_img = Image.fromarray(filler_image)
    
    img = ImageTk.PhotoImage(pil_img)
    return img

class CancelableRunningSimulationThread(threading.Thread):
    def __init__(self, game: Game) -> None:
        super().__init__()
        self.isCanceled = threading.Event()
        self.canDoNext = threading.Event()
        self.canDoNext.set()
        self.game_instance = game
    def run(self) -> None:
        while True:
            self.canDoNext.wait()
            self.canDoNext.clear()
            if self.isCanceled.is_set():
                break
            self.game_instance.lock.acquire(blocking=True, timeout=1)
            self.game_instance.last_grid = self.game_instance.game_grid.copy() # type: ignore
            Game.update_game(self.game_instance)
            self.game_instance.lock.release()
        
        del self
    
    def next(self):
        self.canDoNext.set()
    
    def cancel(self):
        self.isCanceled.set()
    def uncancel(self):
        self.isCanceled.clear()

class CanvasGame(Game):
    def __init__(self, master: Tk) -> None:
        Game.__init__(self, grid_size=(200, 200))
        self.last_grid = self.game_grid.copy()
        
        self.master = master
        self.cell_size = 5
        self.width_cells = self.grid_size[0]
        self.height_cells = self.grid_size[1]
        self.extended_size = (self.grid_size[0] * self.cell_size, self.grid_size[1] * self.cell_size)
        
        self.auto_running = False
        self.fps = 40
        self.simulation_rate = 1100 // self.fps
        self.image = None
        
        self.menubar = Menu(master, tearoff=0)
        self.menubar.add_command(label="Quitter", command=self.quit)
        
        self.simulation_menu = Menu(self.menubar, tearoff=0)
        self.simulation_menu.add_command(label="Valider la position de départ", command=self.start_game)
        self.simulation_menu.add_command(label="Lancer la simulation", command=self.start_auto_run)
        self.simulation_menu.add_command(label="Mettre sur pause", command=self.pause_game)
        self.simulation_menu.add_command(label="Réinitialiser le jeu", command=self.reset_game)
        self.simulation_menu.add_separator()
        self.simulation_menu.add_command(label="Avance de 1", command=partial(CanvasGame.jump_by, self, 1)) # type: ignore
        self.simulation_menu.add_command(label="Avance de 10", command=partial(CanvasGame.jump_by, self, 10)) # type: ignore
        self.simulation_menu.add_command(label="Avance de 50", command=partial(CanvasGame.jump_by, self, 50)) # type: ignore
        self.simulation_menu.add_separator()
        self.simulation_menu.add_command(label="Retour de 1", command=partial(CanvasGame.jump_by, self, -1)) # type: ignore
        self.simulation_menu.add_command(label="Retour de 10", command=partial(CanvasGame.jump_by, self, -10)) # type: ignore
        self.simulation_menu.add_command(label="Retour de 50", command=partial(CanvasGame.jump_by, self, -50)) # type: ignore
        self.simulation_menu.add_separator()
        self.menubar.add_cascade(label='Simulation', menu=self.simulation_menu)
        
        self.menubar.add_command(label="Stop", command=self.pause_game)
        
        master.config(menu=self.menubar)
        
        self.gen_text = Label(master, text="Generation 0")
        self.gen_text.pack()
        
        self.canvas_size = (self.width_cells * self.cell_size, self.height_cells * self.cell_size)
        self.canvas = Canvas(
            master, 
            background="white",
            bg="white", 
            width=self.width_cells * self.cell_size,
            height=self.height_cells * self.cell_size,
            highlightthickness=0,
        )
        self.canvas.pack()
        
        # self.size[0] / 2 => la moitié du nombre de cellules
        # self.width_cells / 2 => la moitié de l'écran en nb de cellules
        self.x_display_pos = round(self.grid_size[0] / 2) - round(self.width_cells / 2)
        self.y_display_pos = round(self.grid_size[1] / 2) - round(self.height_cells / 2)
        print(self.x_display_pos, self.y_display_pos)
        
        self.canvas.bind("<Button-1>", self.click_canvas)
    
    # def write_pixel(self, x, y, force=False):
    #     real_x = x + self.x_display_pos
    #     real_y = y + self.y_display_pos
    #     if not force and self.last_grid[real_x, real_y] == self.game_grid[real_x, real_y]:
    #         return
        
    #     first_point = (x * self.cell_size, y * self.cell_size)
    #     second_point = ((x + 1) * self.cell_size - 1, (y + 1) * self.cell_size - 1)
    #     color = "black" if self.game_grid[self.x_display_pos + x, self.y_display_pos + y] == 1 else "white"
    #     if force:
    #         self.canvas.create_rectangle(first_point, second_point, fill=color, outline=color)
    #     elif color != "white":
    #         self.canvas.create_rectangle(first_point, second_point, fill=color, outline=color)
    
    def get_extanded_corrected_grid(self):
        extanded_image = np.zeros(self.extended_size)
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                # inverse les x et les y sinon cause un bug
                x_start = y * self.cell_size
                x_end = (y + 1) * self.cell_size
                y_start = x * self.cell_size
                y_end = (x + 1) * self.cell_size
                extanded_image[x_start:x_end, y_start:y_end] = self.game_grid[x, y]
        
        return extanded_image
    
    def write_grid(self, force=False):
        img = self.get_extanded_corrected_grid()
        self.image = _photo_image(img)
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        
    
    def jump_by(self, amount: int):
        self.last_grid = self.game_grid.copy()
        target_gen = max(0, self.generation + amount)
        self.get_game_gen(target_gen)
        self.gen_text.configure(text="Generation " + str(self.generation))
        self.write_grid(force=True)
    
    def quit(self):
        self.pause_game()
        self.master.quit()
    
    def click_and_motion(self):
        if self.in_game:
            return
         
        abs_x = self.canvas.winfo_pointerx()
        abs_y = self.canvas.winfo_pointery()
        rel_x = abs_x - self.canvas.winfo_rootx()
        rel_y = abs_y - self.canvas.winfo_rooty()
        
        display_x = rel_x // self.cell_size
        display_y = rel_y // self.cell_size
        
        x = display_x + self.x_display_pos
        y = display_y + self.y_display_pos
        
        x_start = x - self.kernel_distance
        x_end = x + self.kernel_distance + 1
        y_start = y - self.kernel_distance
        y_end = y + self.kernel_distance + 1
        sub_grid = self.game_grid[x_start:x_end, y_start:y_end]
        sub_grid *= -1
        sub_grid += self.kernel
        np.clip(sub_grid, a_min=0, a_max=1)
        self.game_grid[x_start:x_end, y_start:y_end] = sub_grid
        
        
    
    def click_canvas(self, event: Event):
        if self.in_game:
            return
         
        abs_x = self.canvas.winfo_pointerx()
        abs_y = self.canvas.winfo_pointery()
        rel_x = abs_x - self.canvas.winfo_rootx()
        rel_y = abs_y - self.canvas.winfo_rooty()
        
        
        display_x = rel_x // self.cell_size
        display_y = rel_y // self.cell_size
        
        x = display_x + self.x_display_pos
        y = display_y + self.y_display_pos
        try:
            r = self.switch_state((x, y))
            print(r)
        except AssertionError as e:
            pass
        
        self.write_grid(force=True)
    
    def update_game(self):
        if self.auto_running:
            return
        self.last_grid = self.game_grid.copy()
        returned = super().update_game()
        self.gen_text.configure(text="Generation " + str(self.generation))
        self.write_grid(force=True)
        return returned
    
    def start_auto_run(self):
        self.auto_running = True
        self.thread = CancelableRunningSimulationThread(self)
        self.thread.start()
        self.auto_update()
        
    def auto_update(self):
        if self.auto_running is True:
            self.write_grid(force=True)
            self.gen_text.configure(text="Generation " + str(self.generation))
            self.canvas.after(self.simulation_rate, self.auto_update)
            self.thread.next()
    
    def pause_game(self):
        if self.auto_running:
            self.auto_running = False
            self.thread.cancel()
            self.thread.next()
            del self.thread
    
    def reset_game(self):
        self.pause_game()
        self.gen_text.configure(text="Generation 0")
        super().reset_game()
        print("drawing rectangle of dim " + str((self.canvas.winfo_reqwidth(), self.canvas.winfo_reqwidth())))
        self.canvas.create_rectangle((0, 0), (self.canvas.winfo_reqwidth(), self.canvas.winfo_reqwidth()), fill="white", outline="white")
