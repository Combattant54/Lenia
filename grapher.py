import argparse
import matplotlib.pyplot as plt
import numpy as np 

import growth_functions
import sys

x = np.linspace(0., 1., 100)
q = 4
params = []
for arg in sys.argv[2:]:
    params.append(float(arg))
params = np.array(params)
print(params)
print(params[0])

y = growth_functions.register.get(sys.argv[1], growth_functions.poly_quad4)(params, x)

plt.plot(x, y)
plt.axhline(y=0, color='grey', linestyle='dotted')
plt.title(r'Poly_quad4: q=%.2f'%(q))
plt.show()