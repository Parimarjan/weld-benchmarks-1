import argparse
import subprocess as sp
import os

def run_cmd(orig_cmd, name):
    '''
    -- For each cmd, will run it once with numpy and once with weld and output results to the same
    file.
    -- After process_outputs is done, will delete the file.
    '''
    tries = 5
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
	f.close()
    # Let's run the dump-csv script and pass in name. Matches all files with similar name.
    dump_cmd = 'python ./../process_outputs.py -f {f}'.format(f=name)
    dump_cmd = dump_cmd.split()
    process = sp.Popen(dump_cmd)
    process.wait()
    # Cleanup!
    for i in range(tries):
        fname = name + str(i) + '.txt'
        os.remove(fname)

def run_blackscholes(n, p, name):
    os.chdir('blackscholes')
    f = 'bench'
    args = '-n {n} -ie 1 -g 0 -p {p}'.format(n=n, p=p)
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

def run_quasi(n, p, name):
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

# ~100 seconds for numpy
BLACKSCHOLES_ARGS = (10**8)*2 /args.d
run_blackscholes(BLACKSCHOLES_ARGS, 'whatever', 'blackscholes')

# gives it 50-60 secs as we want.
HAVERSINE_SCALE = 200000 / args.d
#run_haversine(HAVERSINE_SCALE, 'whatever', 'haversine')

# Keeps it around ~70 seconds for numpy
NBODY_ARGS = 20000 / args.d
#run_nbody(NBODY_ARGS, 'whatever', 'nbody')

PIXELS = 2048 / args.d
#run_quasi(PIXELS, 'whatever', 'quasi')
