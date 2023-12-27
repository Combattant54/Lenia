import numpy as np

def poly_quad(params: np.ndarray, X: np.ndarray):
    r"""Quadratic polynomial

    .. math::
        y = (q * X * (1 - X))^q

    .. plot::

        import matplotlib.pyplot as plt
        import numpy as np
        from leniax.kernel_functions import poly_quad
        x = np.linspace(0., 1., 100)
        q = 4
        params = np.array([q])
        y = poly_quad(params, x)
        plt.plot(x, y)
        plt.axhline(y=0, color='grey', linestyle='dotted')
        plt.title(r'Poly_quad4: q=%.2f'%(q))
        plt.show()

    Args:
        params: Kernel function parameters
        X: Raw kernel
    """

    q = params[0]

    out = 4 * X * (1 - X)
    out = out**q

    return out

def gauss_bump(params: np.ndarray, X: np.ndarray):
    r"""Gaussian bump function

    .. math::
        y = e^{q * [q - \frac{1}{X * (1 - X)}]}

    .. plot::

        import matplotlib.pyplot as plt
        import numpy as np
        from leniax.kernel_functions import gauss_bump
        x = np.linspace(0., 1., 100)
        q = 4
        params = np.array([q])
        y = gauss_bump(params, x)
        plt.plot(x, y)
        plt.axhline(y=0, color='grey', linestyle='dotted')
        plt.title(r'Gauss bump: q=%.2f'%(q))
        plt.show()

    Args:
        params: Kernel function parameters
        X: Raw kernel
    """
    q = params[0]

    out = q - 1 / (X * (1 - X) + 1e-7)
    out = np.exp(q * out)

    return out