import sys
import numpy as np
import math as m
from random import random
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d
import multiprocessing as mp
import threading

# camera
lower_left_corner = np.array([-2.0, 1.0, -1.0])
horizontal = np.array([4.0, 0.0, 0.0])
vertical = np.array([0.0, 0.0, 2.0])

def random_in_unit_sphere():
    while True:
        p = 2.0 * np.array([random(), random(), random()]) - np.array([1,1,1])
        if np.dot(p,p) >= 1.0: break
    return p

class Lambertian:
    def __init__(self,ax,ay,az):
        self.albedo = np.array((ax,ay,az))

    def scatter(self,origin,hit_point,normal)->bool:
        target = hit_point + normal + random_in_unit_sphere()
        scattered = target - hit_point
        attenuation = self.albedo
        return (True,attenuation,scattered)

class  Metal:
    fuzz = 0.
    def __init__(self,ax,ay,az,f):
        self.fuzz = f
        self.albedo = np.array((ax,ay,az))

    def scatter(self,origin,hit_point,normal)->bool:
        #reflected = 2 * (hit_point + normal)
        reflected = origin - 2 * np.dot(hit_point,normal) * normal
        scattered = reflected + self.fuzz * random_in_unit_sphere()
        attenuation = self.albedo
        return (np.dot(scattered,normal) > 0,attenuation,scattered)

objs = [ #0:center 1:radius 2:metal
    (np.array([0,1,-105.5]),100,Lambertian(0.8,0.8,0.0)),
    (np.array([0,1,0]),0.5,Lambertian(0.8,0.3,0.3)),
    (np.array([1,1,0]), 0.5,Metal(0.8,0.6,0.2,1.0)),
    (np.array([-1,1,0]), 0.5,Metal(1.0,1.0,1.0,0.0)),
]

def ray(origin,direction,objects,depth,hit_rays):
    hit_anything = False
    t_closest = sys.float_info.max
    
    for (sphere_c,sphere_r,metal) in objects:
        oc = origin - sphere_c
        a = np.dot(direction, direction)
        b = 2.0 * np.dot(oc, direction)
        c = np.dot(oc, oc) - sphere_r**2
        d = b**2 - 4*a*c
        
        if d < 0: continue
        t = (-b - m.sqrt(d)) / (2 * a)
        if not (0.001 < t and t < t_closest):
                t = (-b + m.sqrt(d)) / (2 * a)
        if not (0.001 < t and t < t_closest):
                continue
        t_closest = t
        hit_point = origin + t * direction
        normal = (hit_point - sphere_c) / sphere_r
        hit_metal = metal
        hit_anything = True
    color = np.array([0,0,0])
    if hit_anything:
        hit_rays.append((origin,hit_point,depth))
        hit_point_unit = hit_point / m.sqrt(np.dot(hit_point,hit_point))
        (ret,attenuation,scatterd) = hit_metal.scatter(origin,hit_point_unit,normal)
        if depth < 50 and ret:
                color = attenuation * ray(hit_point,scatterd,objects,depth + 1,hit_rays)
    else:
        t_closest = sys.float_info.max
        if depth > 0: hit_rays.append((origin,direction,depth))
        direction_unit = direction / m.sqrt(np.dot(direction,direction))
        t = 0.5 * (direction_unit[2] + 1.0)
        color = (1.0-t) * np.array([1.0, 1.0, 1.0]) + t * np.array([0.5, 0.7, 1.0])
    return color

def run(tasks,nx,ny,ns,pixel_colors,hit_rays):
    for (i,j) in tasks:
        u = i / (nx - 1)
        v = j / (ny - 1)
        direction = lower_left_corner + u * horizontal + v * vertical
        pixel_color = np.array((0,0,0))
        for n in range(ns):
                u = (i + (random() if ns > 1 else 0)) / (nx - 1)
                v = (j + (random() if ns > 1 else 0)) / (ny - 1)
                r = lower_left_corner + u * horizontal + v * vertical
                color = ray(np.array([0,0,0]),r,objs,0,hit_rays)
                pixel_color = pixel_color + color
        pixel_color = pixel_color / ns
        pixel_colors.append((direction,np.sqrt(pixel_color)))