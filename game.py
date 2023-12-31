import numpy as np
from collections import deque, namedtuple
import threading
from functools import partial
import kernels
import growth_functions


class Game:
    Cell = namedtuple("Cell", ["x", "y", "value"])
    kernel_size = (9, 9)
    kernel = kernels.create_gaussian_kernel(size=kernel_size, m=0.3, s=0.2)
    kernel_sum = np.sum(kernel)
    kernel_distance = kernel_size[0] // 2

    G_function = partial(growth_functions.staircase, params=np.array([0.3, 0.1]))
    def __init__(self, grid_size=(100, 100)):
        self.grid_size = grid_size
        self.game_grid = np.ndarray(grid_size, dtype=np.float64)
        self.game_grid[:,:] = False
        self.generation = 0
        self.buffer_size = 64
        self.grid_buffer: deque[np.ndarray] = deque(maxlen=self.buffer_size)
        self.initial_state = None
        self.in_game = False
        self.start_calculation = None
        self.end_calculation = None
        self.alive_cells = []
        self.lock = threading.Lock()
        self.last_grid = None
        self.time_step = 0.1
    
    def update_calculation_area(self, coord):
        if self.start_calculation is None:
            self.start_calculation = [coord[0] - self.kernel_distance, coord[1] - self.kernel_distance]
        elif coord[0] - self.kernel_distance <= self.start_calculation[0] or coord[1] - self.kernel_distance <= self.start_calculation[1]:
            self.start_calculation[0] = min(self.start_calculation[0], coord[0] - self.kernel_distance)
            self.start_calculation[1] = min(self.start_calculation[1], coord[1] - self.kernel_distance)
        
        if self.end_calculation is None:
            self.end_calculation = [coord[0] + self.kernel_distance, coord[1] + self.kernel_distance]
        elif coord[0] + self.kernel_distance >= self.end_calculation[0] or coord[1] + self.kernel_distance >= self.end_calculation[1]:
            self.end_calculation[0] = max(self.end_calculation[0], coord[0] + self.kernel_distance + 1)
            self.end_calculation[1] = max(self.end_calculation[1], coord[1] + self.kernel_distance + 1)

    def switch_state(self, coord):
        assert 0 <= coord[0] < self.grid_size[0]
        assert 0 <= coord[1] < self.grid_size[1]
        
        # self.update_calculation_area(coord)
        
        last_val = self.game_grid[coord]
        self.game_grid[coord[0], coord[1]] = 1 if self.game_grid[coord[0], coord[1]] == 0 else 0
        val = self.game_grid[coord]
        print("setting value from {} to {}".format(last_val, val))
        
        return self.game_grid[coord[0], coord[1]]
    
    def apply_kernel(self, x, y):
        cells = self.game_grid[x-self.kernel_distance:x+self.kernel_distance+1, y-self.kernel_distance:y+self.kernel_distance+1]
        cells = cells * self.kernel
        return np.sum(cells) / self.kernel_sum
    
    def compute_next_gen(self):
        U_cells = np.zeros(self.grid_size)
        for x in range(self.kernel_distance, self.grid_size[0] - self.kernel_distance - 1):
            for y in range(self.kernel_distance, self.grid_size[1] - self.kernel_distance - 1):
                U_cells[x, y] = self.apply_kernel(x, y)
        A_cells = self.G_function(X=U_cells)
        A_cells *= self.time_step
        self.game_grid += A_cells
        
        np.clip(self.game_grid, a_min=0, a_max=1)
        
        return self.game_grid
    
    def update_game(self):
        self.compute_next_gen()
        self.generation += self.time_step
        self.grid_buffer.append(self.game_grid.copy())
        
    def get_game_gen(self, gen_number: int):
        if gen_number < 0:
            return None
        if gen_number == 0:
            return self.initial_state
        
        if gen_number > self.generation:
            while self.generation < gen_number:
                self.update_game()
            return self.game_grid
        
        difference = self.generation - gen_number
        if difference > self.buffer_size:
            message = f"Gen actuelle : {self.generation}; Gen voulue : {gen_number}; Ecart : {difference}; Buffer size : {self.buffer_size}"
            print(message)
            return None
        
        for i in range(difference):
            self.game_grid = self.grid_buffer.pop()
            self.generation -= self.time_step
        
        return self.game_grid
    
    def start_game(self):
        self.initial_state = self.game_grid.copy()
        self.in_game = True
        
    def reset_game(self):
        self.grid_buffer.clear()
        self.game_grid[:, :] = 0
        self.initial_state = None
        self.generation = 0
        self.in_game = False
        self.start_calculation = None
        self.end_calculation = None
        self.alive_cells.clear()
        