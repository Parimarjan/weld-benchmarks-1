import argparse
import subprocess as sp
import os

def run_cmd(orig_cmd, name, only_end_to_end):
    '''
    -- For each cmd, will run it once with numpy and once with weld and output results to the same
    file.
    -- After process_outputs is done, will delete the file.
    '''
    tries = 2
    for i in range(tries):
        # Keep this file for both numpy and weld so can process output easily.
        fname = name + str(i) + '.txt'
        f = open(fname, 'w')
        # Numpy turn
        cmd = list(orig_cmd)
        cmd.append('-numpy')
        cmd.append('1')
        print('**********going to run********: ', cmd)
        process = sp.Popen(cmd, stdout=f)
        process.wait()
        # Weld turn!
        cmd = list(orig_cmd)
        cmd.append('-weld')
        cmd.append('1')
        print('**********going to run********: ', cmd)
        process = sp.Popen(cmd, stdout=f)
        process.wait()
        f.close()
    # Let's run the dump-csv script and pass in name. Matches all files with similar name.
    dump_cmd = 'python ./../process_outputs.py -f {f} -only_end_to_end {}'.format(f=name,
            e=only_end_to_end)
    dump_cmd = dump_cmd.split()
    process = sp.Popen(dump_cmd)
    process.wait()
    # Cleanup!
    for i in range(tries):
        fname = name + str(i) + '.txt'
        os.remove(fname)

def run_blackscholes(n, p, name, only_end_to_end=False):
    os.chdir('blackscholes')
    f = 'bench'
    args = '-n {n} -ie 1 -g 0 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, only_end_to_end)
    os.chdir('..')

def run_nbody(n, p, name, only_end_to_end=False):
    os.chdir('nbody')
    f = 'nbody.py'
    args = '-n {n} -t 1 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, only_end_to_end)
    os.chdir('..')

def run_haversine(s, p, name, only_end_to_end=False):
    os.chdir('haversine')
    f = 'main.py'
    args = '-s {s} -g 1 -p {p}'.format(s=s, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name, only_end_to_end)
    os.chdir('..')

def run_quasi(n, p, name, only_end_to_end=False):
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
    run_cmd(cmd, name, only_end_to_end)
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
BLACKSCHOLES_SUPPORTED_OPS = [np.sqrt, np.divide, np.exp, np.add, np.subtract]

run_blackscholes(BLACKSCHOLES_ARGS, 'whatever', 'blackscholes')

if args.run_incremental:
    # start with no supported ops, and then successively keep adding supported ops.

# ablation studies!
if args.run_ablation:
    run_blackscholes(BLACKSCHOLES_ARGS, 'fusion', 'blackscholes')
    run_blackscholes(BLACKSCHOLES_ARGS, 'vector', 'blackscholes')
    run_blackscholes(BLACKSCHOLES_ARGS, 'infer', 'blackscholes')
    run_blackscholes(BLACKSCHOLES_ARGS/args.d, 'predicat', 'blackscholes_predicat')
    run_blackscholes(BLACKSCHOLES_ARGS/args.d, 'circuit', 'blackscholes_circuit')

# gives it 50-60 secs as we want.
HAVERSINE_SCALE = 10**5 / args.d
run_haversine(HAVERSINE_SCALE, 'whatever', 'haversine')

if args.run_ablation:
    run_haversine(HAVERSINE_SCALE, 'fusion', 'haversine')
    run_haversine(HAVERSINE_SCALE, 'vector', 'haversine')
    run_haversine(HAVERSINE_SCALE, 'infer', 'haversine')
    run_haversine(HAVERSINE_SCALE, 'predicate', 'haversine_predicate')
    run_haversine(HAVERSINE_SCALE, 'circuit', 'haversine_circuit')

# Keeps it around ~70 seconds for numpy
NBODY_ARGS = 25000 / args.d

run_nbody(NBODY_ARGS, 'whatever', 'nbody')

if args.run_ablation:
    run_nbody(NBODY_ARGS, 'fusion', 'nbody')
    run_nbody(NBODY_ARGS, 'vector', 'nbody')
    run_nbody(NBODY_ARGS, 'infer', 'nbody')
    run_nbody(NBODY_ARGS, 'predicate', 'nbody_predicate')
    run_nbody(NBODY_ARGS, 'circuit', 'nbody_circuit')

PIXELS = 2048 / args.d
run_quasi(PIXELS, 'whatever', 'quasi')

if args.run_ablation:
    run_quasi(PIXELS, 'fusion', 'quasi')
    run_quasi(PIXELS, 'vector', 'quasi')
    run_quasi(PIXELS, 'infer', 'quasi')
    run_quasi('predicate', 'quasi')
    run_quasi('circuit', 'quasi')
