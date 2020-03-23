import numpy as np
import math as m
from random import random
import sys
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d
import threading
import multiprocessing as mp    # 多进程的模块

if __name__ == '__main__':        
        mp.freeze_support()

        nx = 20 * 4
        ny = 10 * 4
        ns = 100

        num_worker = 4
        rays = []

        window = plt.figure()
        view = window.gca(projection='3d')
        view.set_aspect('equal')    
        ts = []
        ios = []
        for j in range(ny):
                for i in range(nx):
                        ios.append((i,j))
        import work
        
        for tasks in np.array_split(ios,num_worker):
                pixel_colors = mp.Manager().list()
                hit_rays = mp.Manager().list()
                print('tasks:',len(tasks))
                p = mp.Process(target=work.run,args=(tasks,nx,ny,ns,pixel_colors,hit_rays))
                ts.append((p,pixel_colors,hit_rays))
                p.start()
        plt.ion()

        def update(pixel_colors,hit_rays):
                screen_x = [-2,2,-2,2]
                screen_y = [1,1,1,1]
                screen_z = [1,1,-1,-1]
                
                plt.cla()
                view.scatter(screen_x,screen_y,screen_z,s=0.5)
                view.scatter([0],[0],[0],c=[(0,0,0)])
                #hit_rays=[]
                for (sc,sp,depth) in hit_rays:
                        #if depth is 0 : continue
                        view.plot([sc[0],sp[0]],[sc[1],sp[1]],[sc[2],sp[2]])
                if len(pixel_colors) > 0:
                        pixels = np.array(pixel_colors)
                        pixel = pixels[:,0]
                        view.scatter(pixel[:,0],pixel[:,1],pixel[:,2],c=pixels[:,1],marker=',')
                view.set(xlim=(-2,2),ylim=(-2,2),zlim=(-2,2))
                plt.pause(.2)
                
        colors = []
        rays = []
        for (p,pixels_colors,hit_rays) in ts:
                p.join()
                colors.extend(pixels_colors)
                rays.extend(hit_rays)
                print('rays:',len(rays))
        update(colors,[])

        plt.ioff()
        plt.show()
