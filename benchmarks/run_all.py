import argparse
import subprocess as sp
import os

def run_cmd(orig_cmd, name):
    tries = 2
    for i in range(tries):
        cmd = list(orig_cmd)
        fname = name + str(i) + '.txt'
        f = open(fname, 'w')
        print('**********going to run********: ', cmd)
        process = sp.Popen(cmd, stdout=f)
        f.close()
        process.wait()

    # Let's run the dump-csv script and pass in name
    dump_cmd = 'python ./../process_outputs.py -f {f}'.format(f=name)
    dump_cmd = dump_cmd.split()
    process = sp.Popen(dump_cmd)
    process.wait()

def run_blackscholes(n, p, name):
    os.chdir('blackscholes')
    f = 'bench'
    args = '-n {n} -ie 0 -g 1 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name)
    os.chdir('..')

def run_nbody(n, p, name):
    os.chdir('nbody')
    f = 'nbody.py'
    args = '-n {n} -t 1 -p {p}'.format(n=n, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name)
    os.chdir('..')

def run_haversine(s, p, name):
    os.chdir('haversine')
    f = 'main.py'
    args = '-s {s} -g 1 -p {p}'.format(s=s, p=p)
    cmd = 'python {file} {args}'.format(file=f, args=args)
    cmd = cmd.split()
    run_cmd(cmd, name)
    os.chdir('..')


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--d", type=int, required=False,
                    default=1, help="divide all size args by d")
args = parser.parse_args()

BLACKSCHOLES_ARGS = (10**8)*2 /args.d
run_blackscholes(BLACKSCHOLES_ARGS, 'whatever', 'blackscholes')
# ablation studies!
run_blackscholes(BLACKSCHOLES_ARGS, 'fusion', 'blackscholes_fusion')
run_blackscholes(BLACKSCHOLES_ARGS, 'vector', 'blackscholes_vector')
run_blackscholes(BLACKSCHOLES_ARGS, 'infer', 'blackscholes_infer')

# run_blackscholes(BLACKSCHOLES_ARGS/args.d, 'predicat', 'blackscholes_predicat')
# run_blackscholes(BLACKSCHOLES_ARGS/args.d, 'circuit', 'blackscholes_circuit')

HAVERSINE_SCALE = 10^6 / args.d
run_haversine(HAVERSINE_SCALE, 'whatever', 'haversine')
# ablation studies!
run_haversine(HAVERSINE_SCALE, 'fusion', 'haversine_fusion')
run_haversine(HAVERSINE_SCALE, 'vector', 'haversine_vector')
run_haversine(HAVERSINE_SCALE, 'infer', 'haversine_infer')
# run_haversine(HAVERSINE_SCALE, 'predicate', 'haversine_predicate')
# run_haversine(HAVERSINE_SCALE, 'circuit', 'haversine_circuit')

NBODY_ARGS = 10000*2 / args.d
run_nbody(NBODY_ARGS, 'whatever', 'nbody')
run_nbody(NBODY_ARGS, 'fusion', 'nbody_fusion')
run_nbody(NBODY_ARGS, 'vector', 'nbody_vector')
run_nbody(NBODY_ARGS, 'infer', 'nbody_infer')
# run_nbody(NBODY_ARGS, 'predicate', 'nbody_predicate')
# run_nbody(NBODY_ARGS, 'circuit', 'nbody_circuit')

# run_quasi()
