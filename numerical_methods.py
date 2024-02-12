import numpy as np


def rkNext(x, h, f):
    k1 = f(x)
    k2 = f(x + h*k1/2)
    k3 = f(x + h*k2/2)
    k4 = f(x + h*k3)

    return x + (h/6)*(k1 + 2*k2 + 2*k3 + k4)



def RungeKutta(tmin, tmax, func, t_init, x_init):
    h = (tmax-tmin) / 1000

    
    after = []
    before = []
    t_after = []
    t_before = []

    t = t_init + h
    x_last = x_init
    while t < tmax:
        x_new = rkNext(x_last, h, func)
        after.append(x_new)
        t_after.append(t)

        x_last = x_new
        t += h

    
    t = t_init - h
    x_last = x_init
    while t > tmin:
        x_new = rkNext(x_last, -h, func)
        before.append(x_new)
        t_before.append(t)

        x_last = x_new
        t -= h
    before_reversed = before[::-1]  
    xs = before_reversed + [x_init] + after


    before_t_reversed = t_before[::-1]  
    ts = before_t_reversed + [t_init] + t_after
    return (ts , xs)


def Euler(tmin, tmax, func, t_init, x_init):
    h = (tmax-tmin) / 1000

    xs_after = [x_init]
    ts_after = np.arange(t_init, tmax + h, h)
    for _ in ts_after:
        x_n = xs_after[-1]
        xs_after.append(x_n + func(x_n) * h)
    
    xs_before = [x_init]
    ts_before = np.arange(t_init, tmin - h, -h)
    for _ in ts_before:
        x_n = xs_before[-1]
        xs_before.append(x_n - func(x_n) * h)

    return np.append(ts_before[::-1][:-1], ts_after), xs_before[::-1][1:-1] + xs_after[:-1]


class IntegralCurve:
    def __init__(self, func, t_init, x_init, *, method=RungeKutta):
        self.func = func
        self.method = method
        self.t_init = t_init
        self.x_init = x_init

    def __call__(self, tmin, tmax):
        return self.method(tmin, tmax, self.func, self.t_init, self.x_init)