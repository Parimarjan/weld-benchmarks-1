# import pandas as pd
import numpy as np
from math import *
import time
from weldnumpy import weldarray
import weldnumpy as wn
import argparse
import csv
import ast
import json
import pandas as pd

# for group 
import grizzly.grizzly as gr
from grizzly.lazy_op import LazyOpResult

# ### Read in the data

# In[52]:

df = pd.read_csv('data', encoding='cp1252')

# ## Haversine definition
def haversine(lat1, lon1, lat2, lon2):
    
    miles_constant = 3959.0
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2]) 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2.0 * np.arcsin(np.sqrt(a)) 
    mi = miles_constant * c
    return mi

def gen_data(lat, lon, scale=10):
    '''
    Generates the array replicated X times.
    '''
    np.random.seed(1)
    new_lat = []
    new_lon = []
    for i in xrange(len(lat)*scale):
        index = i % len(lat) 
        l1 = lat[index]
        l2 = lon[index]
        new_lat.append(l1 + np.random.rand())
        new_lon.append(l2 + np.random.rand())
    
    # TODO: fix this.
    # with open('lats.json', 'w') as fp:
        # json.dump(new_lat, fp) 
    # with open('lons.json', 'w') as fp:
        # json.dump(new_lon, fp) 

    return np.array(new_lat), np.array(new_lon)

def gen_data2(lat, lon, scale=10):
    '''
    generates 2 pairs of arrays so can pass two arrays to havesrine. 
    '''
    pass

def generate_lazy_op_list(arrays):
    ret = []
    for a in arrays:
        lazy_arr = LazyOpResult(a.weldobj, a._weld_type, 1)
        ret.append(lazy_arr)
    return ret

def compare(R, R2):
    
    if isinstance(R2, weldarray):
        R2 = R2.evaluate()

    mistakes = 0
    R = R.flatten()
    R2 = R2.view(np.ndarray).flatten()
    
    assert R.dtype == R2.dtype, 'dtypes must match!'
    
    assert np.allclose(R, R2)
    # assert np.array_equal(R, R2)

def print_args(args):
    d = vars(args)
    print('params: ', str(d))

def read_data():
    # data = []
    # with open(name, "rb") as f:
        # reader = csv.reader(f, delimiter="\t")
        # for i, line in enumerate(reader):
            # x = line[0].split(',')
            # x = [np.float64(l) for l in x]
            # data.append(x)

    return json.load(open('lats.json')), json.load(open('lons.json'))

def run_haversine_with_scalar(args):
    orig_lat = df['latitude'].values
    orig_lon = df['longitude'].values

    if args.use_numpy:
        ########### Numpy stuff ############
        lat, lon = gen_data(orig_lat, orig_lon, scale=args.scale)
        # lat, lon = read_data()
        print('num rows in lattitudes: ', len(lat))
        start = time.time()
        dist1 = haversine(40.671, -73.985, lat, lon)
        end = time.time()
        print('****************************')
        print('numpy took {} seconds'.format(end-start))
        print('****************************')
    else:
        print('Not running numpy')
    

    if args.use_weld:
        ####### Weld stuff ############
        lat2, lon2 = gen_data(orig_lat, orig_lon, scale=args.scale)
        print('num rows in lattitudes: ', len(lat2))
        lat2 = weldarray(lat2)
        lon2 = weldarray(lon2)
        start = time.time()
        dist2 = haversine(40.671, -73.985, lat2, lon2) 
        if args.use_group:
            print('going to use group')
            lazy_ops = generate_lazy_op_list([dist2])
            dist2 = gr.group(lazy_ops).evaluate(True, passes=wn.CUR_PASSES)[0]
        else:
            dist2 = dist2.evaluate()

        end = time.time()
        print('****************************')
        print('weld took {} seconds'.format(end-start))
        print('****************************')
        print('END')
    else:
        print('Not running weld')
    
    if args.use_numpy and args.use_weld:
        compare(dist1, dist2)

parser = argparse.ArgumentParser(
    description="give num_els of arrays used for nbody"
)
parser.add_argument('-s', "--scale", type=int, required=True,
                    help="how much to scale up the orig dataset?")
parser.add_argument('-g', "--use_group", type=int, default=0,
                    help="use group or not")
parser.add_argument('-p', "--remove_pass", type=str, 
                    default="whatever_string", help="will remove the pass containing this str")
parser.add_argument('-numpy', "--use_numpy", type=int, required=False, default=0,
                    help="use numpy or not in this run")
parser.add_argument('-weld', "--use_weld", type=int, required=False, default=0,
                    help="use weld or not in this run")

args = parser.parse_args()
print_args(args)
wn.remove_pass(args.remove_pass)
print('Passes: ', wn.CUR_PASSES)
run_haversine_with_scalar(args)
