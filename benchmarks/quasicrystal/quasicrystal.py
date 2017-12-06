# -*- coding: utf-8 -*-
# from benchpress import util
import bohrium as np
import numpy_force as np2
import time
import argparse

def run(args, use_weld):
    # k = np.float64(args.k)
    k = args.k
    # TODO: Test timing from the start, but this just seems to be setup code.
    # stripes = np.float64(args.stripes) 
    stripes = args.stripes
    N = args.n
    phases  = np2.arange(0, 2*np.pi, 2*np.pi/args.times)
    image   = np.empty((N, N), dtype=np.float64)
    d       = np2.arange(-N/2, N/2, dtype=np.float64)
        
    xv, yv = np.meshgrid(d, d)
    
    start = time.time()
    # TODO: FIXME --> can we support this in weld? Right now it offloads it.
    theta  = np.arctan2(yv, xv)

    a = xv**2 + yv**2
    # just to remove 0's from a, and stop numpy from complaining.
    # TODO: Maybe remove this since it was not there in original.
    a += 1.0
    r      = np.log(np.sqrt(a))
    
    # TODO: could try to intercept the arange call as well?
    tmp = np2.arange(0, np.pi, np.pi/k)
    
    r.view(np.ndarray)[np.isinf(r) == True] = 0

    tcos   = theta * np.cos(tmp)[:, np.newaxis, np.newaxis]
    rsin   = r * np.sin(tmp)[:, np.newaxis, np.newaxis]
    inner  = (tcos - rsin) * stripes
    
    
    cinner = np.cos(inner)
    sinner = np.sin(inner)
    
    for i, phase in enumerate(phases):
        print(i)
        tmp2 = cinner * np.cos(phase) - sinner * np.sin(phase)
        image[:] = np.sum(tmp2) + k
	print(np.sum(image))

    end = time.time()
    print('*****************************')
    print('bohrium took time = ', end-start)
    print('*****************************')
    return image

def print_args(args):
    d = vars(args)
    print('params: ', str(d))

def main():
    parser = argparse.ArgumentParser(
        description="give num_els of arrays used for nbody"
    )
    parser.add_argument('-k', "--k", type=int, required=True,
                        help="number of plane waves")
    parser.add_argument('-s', "--stripes", type=int, required=True,
                        help="number of stripes per wave")
    parser.add_argument('-n', "--n", type=int, required=True,
                        help="image size in pixels")
    parser.add_argument('-t', "--times", type=int, required=True,
                        help="number of iterations")
    parser.add_argument('-numpy', "--use_numpy", type=int, required=False, default=0,
                        help="use numpy or not in this run")
    parser.add_argument('-weld', "--use_weld", type=int, required=False, default=0,
                        help="use weld or not in this run")
    parser.add_argument('-p', "--remove_pass", type=str, 
                        default="whatever_string", help="will remove the pass containing this str")

    args = parser.parse_args()
    print_args(args)
    
    img1 = run(args, False)

if __name__ == "__main__":
    main()
