from expression_parser import *
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
