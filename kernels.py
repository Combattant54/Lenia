import numpy as np
import math
import functions
import growth_functions

def distance_point(a, b):
    distance = math.sqrt( (a[0] - b[0])**2 + (a[1] - b[1])**2 )
    return distance
    

def create_gaussian_kernel(size=(11, 11),  m=0.5, s=0.05):
    kernel = np.zeros(size)
    
    center = (size[0] // 2, size[1] // 2)
    kernel[center[0], center[1]] = 0
    
    
    for x in range(size[0]):
        for y in range(size[1]):
            distance = distance_point((x, y), center)
            kernel[x, y] = distance

    kernel /= np.max(kernel)
    kernel = growth_functions.gaussian_target(np.array([m, s]), kernel)
    return kernel
    