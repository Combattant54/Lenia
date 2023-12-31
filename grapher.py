import argparse
import matplotlib.pyplot as plt
import numpy as np 

import growth_functions
import kernels
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

exit(0)

fig, plots = plt.subplots(4, 4)

for x_i, x in enumerate(range(4)):
    for y_i, y in enumerate(range(4)):
        m = 0.2 + 0.05 * x
        s = 0.18 + 0.03 * y
        kernel = kernels.create_gaussian_kernel(size=(51, 51), m=m, s=s)
        plots[x_i, y_i].imshow(kernel, cmap="gray")

# le kernel définitif
fig = plt.figure()
kernel = kernels.create_gaussian_kernel(size=(15, 15), m=0.25, s=0.2)
fig.add_subplot().imshow(kernel)


plt.show()