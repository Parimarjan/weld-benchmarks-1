import argparse
import subprocess as sp
import os
import time
import csv
import numpy as np

def run_cmd(orig_cmd, name, remove_ops=0, add_ops=''):
    '''
    -- For each cmd, will run it once with numpy and once with weld and output results to the same
    file.
    -- After process_outputs is done, will delete the file.
    '''
    tries = 5
    use_numpy = False
    print('add ops = ', add_ops)
    # kinda weird hacky stuff, need to see if I can make this right.
    for c in orig_cmd:
	if c == "All":
		use_numpy = True
    if "blackschole" in name:	
	use_numpy = True

    for i in range(tries):
        # Keep this file for both numpy and weld so can process output easily.
	print("i = ", i)
        fname = name + str(i) + '.txt'
        f = open(fname, 'w')
        cmd = list(orig_cmd)
	if use_numpy:
		cmd.append('-numpy')
		cmd.append('1')
        cmd.append('-weld')
        cmd.append('1')

        if remove_ops:
            cmd.append('-remove_ops')
            cmd.append('1')
            cmd.append('-add_ops')
            cmd.append(add_ops)

        print('**********going to run********: ', cmd)
        process = sp.Popen(cmd, stdout=f, stderr=f)
        #process = sp.Popen(cmd)
        process.wait()
	print("process over!")
        f.close()
    # Let's write stuff there first.

    # Let's run the dump-csv script and pass in name. Matches all files with similar name.
    dump_cmd = 'python ./../process_outputs.py -f {f} '.format(f=name)

    dump_cmd = dump_cmd.split()
    process = sp.Popen(dump_cmd)
    process.wait()
    # Cleanup!
    for i in range(tries):
        fname = name + str(i) + '.txt'
        os.remove(fname)

def run_blackscholes(n, p, name, **kwargs):
    os.chdir('blackscholes')
    f = 'bench'
    args = '-n {n} -ie 0 -g 1 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, **kwargs)
    os.chdir('..')

def run_blackscholes_no_group(n, p, name, **kwargs):
    os.chdir('blackscholes')
    f = 'bench'
    args = '-n {n} -ie 1 -g 0 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, **kwargs)
    os.chdir('..')

def run_nbody(n, p, name, **kwargs):
    os.chdir('nbody')
    f = 'nbody.py'
    args = '-n {n} -t 1 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, **kwargs)
    os.chdir('..')

def run_haversine(s, p, name, **kwargs):
    os.chdir('haversine')
    f = 'main.py'
    args = '-s {s} -g 0 -p {p}'.format(s=s, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, **kwargs)
    os.chdir('..')

def run_quasi(n, p, name, **kwargs):
    os.chdir('quasicrystal')
    f = 'quasicrystal.py'
    # TODO: loop over different options here?
    # FIXME: Are these values too unrealistic?!!!
    k = 30.0
    s = 100.0
    t = 1
    args = '-k {k} -s {s} -n {n} -t {t} -p {p}'.format(k=k, s=s, t=t, n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, *kwargs)
    os.chdir('..')

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--d", type=int, required=False,
                    default=1, help="divide all size args by d")
parser.add_argument("-run_ablation", type=int, required=False,
                    default=0, help="run ablation studies?")
parser.add_argument("-run_incremental", type=int, required=False,
                    default=0, help="run ablation studies?")

args = parser.parse_args()

# ~100 seconds for numpy
BLACKSCHOLES_ARGS = (10**8)*2 /args.d
# TODO: erf.
#BLACKSCHOLES_SUPPORTED_OPS = [np.sqrt.__name__, np.log.__name__, np.divide.__name__, np.exp.__name__, 'erf', np.add.__name__, np.subtract.__name__, np.multiply.__name__]
BLACKSCHOLES_SUPPORTED_OPS = [np.subtract.__name__, np.exp.__name__, np.add.__name__, 'erf', np.divide.__name__, np.sqrt.__name__, np.log.__name__, np.multiply.__name__]

FILE_NAME = 'bs'
# run_blackscholes(BLACKSCHOLES_ARGS, 'All', FILE_NAME)

if args.run_incremental:
    # first after removing all ops. 
    run_blackscholes(BLACKSCHOLES_ARGS, 'All', FILE_NAME, remove_ops=1, add_ops='')
    ops = ''
    for i, _ in enumerate(BLACKSCHOLES_SUPPORTED_OPS):
        # keep building the ops string and run it.
        op = BLACKSCHOLES_SUPPORTED_OPS[len(BLACKSCHOLES_SUPPORTED_OPS) -1 -i]
        ops += op + ','
        run_blackscholes(BLACKSCHOLES_ARGS, 'All', FILE_NAME, remove_ops=1, add_ops=ops)

if args.run_ablation:
    run_blackscholes(BLACKSCHOLES_ARGS, 'fusion', FILE_NAME)
    run_blackscholes(BLACKSCHOLES_ARGS, 'vectorize', FILE_NAME)
    run_blackscholes(BLACKSCHOLES_ARGS, 'infer-size', FILE_NAME)
    run_blackscholes(BLACKSCHOLES_ARGS/args.d, 'predicate', FILE_NAME)
    run_blackscholes_no_group(BLACKSCHOLES_ARGS, 'nogroup', FILE_NAME)
    run_blackscholes(BLACKSCHOLES_ARGS/args.d, 'circuit', FILE_NAME)

# gives it 50-60 secs as we want.
HAVERSINE_SCALE = 200000 / args.d
FILE_NAME = 'hs' 
HAVERSINE_SUPPORTED_OPS = [np.add.__name__,np.sqrt.__name__, np.arcsin.__name__,np.cos.__name__, 
 np.divide.__name__, np.sin.__name__, np.subtract.__name__, np.multiply.__name__]

#run_haversine(HAVERSINE_SCALE, 'All', FILE_NAME)

if args.run_incremental:
    # first after removing all ops. 
    run_haversine(HAVERSINE_SCALE, 'Whatever', FILE_NAME, remove_ops=1, add_ops='')
    ops = ''
    for i, _ in enumerate(HAVERSINE_SUPPORTED_OPS):
        # keep building the ops string and run it.
        op = HAVERSINE_SUPPORTED_OPS[len(HAVERSINE_SUPPORTED_OPS) -1 -i]
        ops += op + ','
        run_haversine(HAVERSINE_SCALE, 'Whatever', FILE_NAME, remove_ops=1, add_ops=ops)

if args.run_ablation:
    run_haversine(HAVERSINE_SCALE, 'fusion', FILE_NAME)
    run_haversine(HAVERSINE_SCALE, 'vectorize', FILE_NAME)
    run_haversine(HAVERSINE_SCALE, 'infer', FILE_NAME)
    run_haversine(HAVERSINE_SCALE, 'predicate', FILE_NAME)
    run_haversine(HAVERSINE_SCALE, 'circuit', FILE_NAME)


# Keeps it around ~70 seconds for numpy
NBODY_ARGS = 20000 / args.d
FILE_NAME = 'nb'
#run_nbody(NBODY_ARGS, 'All', FILE_NAME)

if args.run_ablation:
    run_nbody(NBODY_ARGS, 'fusion', FILE_NAME)
    run_nbody(NBODY_ARGS, 'vector', FILE_NAME)
    run_nbody(NBODY_ARGS, 'infer', FILE_NAME)
    run_nbody(NBODY_ARGS, 'predicate', FILE_NAME)
    run_nbody(NBODY_ARGS, 'circuit', FILE_NAME)

# PIXELS = 2048 / args.d
# run_quasi(PIXELS, 'All', 'quasi')
if args.run_ablation:
    pass
    #run_quasi(PIXELS, 'fusion', 'quasi')
    #run_quasi(PIXELS, 'vector', 'quasi')
    #run_quasi(PIXELS, 'infer', 'quasi')

