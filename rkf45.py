"""Runge-Kutta-Fehlberg (RKF45) adaptive ODE solver.

Manual implementation of the Fehlberg coefficients with adaptive step-size
control. No SciPy used for the core algorithm.
"""
from typing import Callable, List, Dict


# Fehlberg coefficients
A2 = 1/4
A3, B32 = 3/8, 9/32
B31 = 3/32
A4 = 12/13
B41, B42, B43 = 1932/2197, -7200/2197, 7296/2197
A5 = 1.0
B51, B52, B53, B54 = 439/216, -8.0, 3680/513, -845/4104
A6 = 1/2
B61, B62, B63, B64, B65 = -8/27, 2.0, -3544/2565, 1859/4104, -11/40

# 4th-order solution coefficients (y)
C1, C3, C4, C5 = 25/216, 1408/2565, 2197/4104, -1/5
# 5th-order solution coefficients (z)
D1, D3, D4, D5, D6 = 16/135, 6656/12825, 28561/56430, -9/50, 2/55


def solve_rkf45(
    f: Callable[[float, float], float],
    t0: float,
    y0: float,
    t_end: float,
    h: float = 0.1,
    tol: float = 1e-6,
    h_min: float = 1e-6,
    h_max: float = 1.0,
    max_steps: int = 10000,
) -> List[Dict]:
    """Solve dy/dt = f(t, y), y(t0) = y0, on [t0, t_end].

    Returns a list of step records with keys:
      step, t, y, h, error, accepted
    """
    results: List[Dict] = []
    t, y = t0, y0
    results.append({"step": 0, "t": t, "y": y, "h": h, "error": 0.0, "accepted": True})

    step = 0
    while t < t_end and step < max_steps:
        if t + h > t_end:
            h = t_end - t

        k1 = h * f(t, y)
        k2 = h * f(t + A2 * h, y + (1/4) * k1)
        k3 = h * f(t + A3 * h, y + B31 * k1 + B32 * k2)
        k4 = h * f(t + A4 * h, y + B41 * k1 + B42 * k2 + B43 * k3)
        k5 = h * f(t + A5 * h, y + B51 * k1 + B52 * k2 + B53 * k3 + B54 * k4)
        k6 = h * f(t + A6 * h, y + B61 * k1 + B62 * k2 + B63 * k3 + B64 * k4 + B65 * k5)

        y4 = y + C1 * k1 + C3 * k3 + C4 * k4 + C5 * k5
        y5 = y + D1 * k1 + D3 * k3 + D4 * k4 + D5 * k5 + D6 * k6

        error = abs(y5 - y4)

        if error <= tol or h <= h_min:
            t += h
            y = y5
            step += 1
            results.append({
                "step": step, "t": t, "y": y, "h": h,
                "error": error, "accepted": True,
            })

        # Adaptive step size
        if error == 0:
            s = 4.0
        else:
            s = 0.84 * (tol * h / error) ** 0.25
        h = max(h_min, min(h_max, h * s))

    return results
