import pandas as pd
import numpy as np
from math import *
import time
from weldnumpy import weldarray
import argparse

# for group 
import grizzly.grizzly as gr
from grizzly.lazy_op import LazyOpResult

# ### Read in the data

# In[52]:

df = pd.read_csv('new_york_hotels.csv', encoding='cp1252')
# df.head()


# # ## Benchmarking example

# # #### Define the normalization function

# # In[54]:

# def normalize(df, pd_series):
    # pd_series = pd_series.astype(float)

    # # Find upper and lower bound for outliers
    # avg = np.mean(pd_series)
    # sd  = np.std(pd_series)
    # lower_bound = avg - 2*sd
    # upper_bound = avg + 2*sd

    # # Collapse in the outliers
    # df.loc[pd_series < lower_bound , "cutoff_rate" ] = lower_bound
    # df.loc[pd_series > upper_bound , "cutoff_rate" ] = upper_bound

    # # Finally, take the log
    # normalized_price = np.log(df["cutoff_rate"].astype(float))
    
    # return normalized_price


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
    
    # this loop takes ages to run so just avoiding it.
    # for i, r in enumerate(R):
        # if not np.isclose(R[i], R2[i]):
        # if we use exact match, then sometimes things seem to be different many decimal places
        # down...
        # if R[i] != R2[i]:
            # mistakes += 1
            # print('R[i] : ', R[i])
            # print('R2[i]: ', R2[i]) 
    # if mistakes != 0:
        # print('mistakes % = ', mistakes / float(len(R)))
    # else:
        # print('mistakes = 0')
    
    assert np.allclose(R, R2)
    # assert np.array_equal(R, R2)


def run_haversine_with_scalar(args):
    orig_lat = df['latitude'].values
    orig_lon = df['longitude'].values
    print('orig shape: ', orig_lat.shape)

    ########### Numpy stuff ############
    lat, lon = gen_data(orig_lat, orig_lon, scale=args.scale)
    start = time.time()
    dist1 = haversine(40.671, -73.985, lat, lon)
    end = time.time()
    print('numpy haversine stuff took {} seconds'.format(end-start))

    ####### Weld stuff ############
    lat2, lon2 = gen_data(orig_lat, orig_lon, scale=args.scale)
    lat2 = weldarray(lat2)
    lon2 = weldarray(lon2)

    # assert np.array_equal(lat, lat2)

    start = time.time()
    dist2 = haversine(40.671, -73.985, lat2, lon2)
    
    if args.use_group:
        print('going to use group!!!!')
        lazy_ops = generate_lazy_op_list([dist2])
        dist2 = gr.group(lazy_ops).evaluate(True)[0]
    else:
        dist2 = dist2.evaluate()

    end = time.time()
    print('weldnumpy haversine stuff took {} seconds'.format(end-start))
    
    compare(dist1, dist2)
    # assert np.allclose(dist1, dist2)
    # assert np.array_equal(dist1, dist2)

parser = argparse.ArgumentParser(
    description="give num_els of arrays used for nbody"
)
parser.add_argument('-s', "--scale", type=int, required=True,
                    help="how much to scale up the orig dataset?")
parser.add_argument('-g', "--use_group", type=int, default=0,
                    help="use group or not")

args = parser.parse_args()

run_haversine_with_scalar(args)
