import argparse
import re
import os
import csv

def get_time_from_string(string):
    '''
    '''
    # matches scientific notation and stuff.
    numbers = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?",
            string)
    # all the things we are printing so far has just 1 num.
    if len(numbers) >= 1:
        return float(numbers[0])
    else:
        return None

def process_file(f):
    global params
    compile_run = []
    encode_run = []
    decode_run = []
    weld_runtimes = []
    weld_total = 0
    numpy_total = 0

    with open(f) as fp:
        print('********************************************')
        print('f = ', f)
        for line in fp:
            time = get_time_from_string(line)
            if 'END' in line:
                break 
            if 'param' in line:
                params = line
            # Printing out threads from weldobj right now.
            if 'threads' in line and time:
                if 'Threads' not in params:
                    params += ' Threads: ' + str(time)
            elif 'weld took' in line and time:
                assert weld_total == 0
                weld_total = time
            elif 'numpy took' in line and time:
                assert numpy_total == 0
                numpy_total = time
            elif 'compile' in line and time:
                compile_run.append(time)
            elif 'Python->Weld' in line and time:
                encode_run.append(time)
            elif 'Weld->Python' in line and time:
                decode_run.append(time)
            elif 'Weld:' in line and time:
                weld_runtimes.append(time)
        print('********************************************')

    assert len(compile_run) == len(encode_run) == len(decode_run) == len(weld_runtimes)

    print('Numpy: ', numpy_total)
    numpys.append(numpy_total)
    print('compile_run = ', sum(compile_run))
    compiles.append(sum(compile_run))
    print('encode_run = ', sum(encode_run))
    encodes.append(sum(encode_run))
    print('decode_run = ', sum(decode_run))
    decodes.append(sum(decode_run))
    print('weld runtimes = ', sum(weld_runtimes))
    welds.append(sum(weld_runtimes))
    total_only_weld = sum(compile_run) + sum(encode_run) + sum(decode_run) + sum(weld_runtimes)
    print('numpy offload = ', weld_total - total_only_weld)
    numpy_offloads.append(weld_total - total_only_weld)
    print('weld end to end = ', weld_total)
    weld_totals.append(weld_total)

def insert_header(header):
    dumpster.writerow(header)

def insert_row(name, vals):
    row = []
    row.append(args.file)   # should be something like benchmark name
    row.append(name)
    # params
    row.append(params)
    # each timings
    row += vals
    dumpster.writerow(row)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=False,
                   help="output file pattern to parse") 
parser.add_argument("-d", "--dir", type=str, required=False, default='./',
                   help="output file pattern to parse") 

args = parser.parse_args()

# Global lists for each of the rows. Each element in the list will represent a new trial (new
# column)
numpys = []
compiles = []
encodes = []
decodes = []
welds = []
numpy_offloads = []
weld_totals = []
params = ''

to_process = []
for f in os.listdir(args.dir):
    print(f)
    if args.file in f and '.txt' in f:
        print f
        full_f = os.path.join(args.dir, f)
        to_process.append(full_f)

for f in to_process:
    process_file(f)

assert len(numpys) == len(compiles) == len(encodes) == len(decodes) == len(welds) == \
len(numpy_offloads) == len(weld_totals)
print('num trials = ', len(numpys))

compiles.insert(0, float(sum(compiles)) / len(compiles))
numpys.insert(0, float(sum(numpys)) / len(numpys))
encodes.insert(0, float(sum(encodes)) / len(encodes))
decodes.insert(0, float(sum(decodes)) / len(decodes))
welds.insert(0, float(sum(welds)) / len(welds))
numpy_offloads.insert(0, float(sum(numpy_offloads)) / len(numpy_offloads))
weld_totals.insert(0, float(sum(weld_totals)) / len(weld_totals))

# CSV dump time!
name = args.file + '.csv'
file_name = os.path.join(args.dir, name)
dumpster = csv.writer(open(file_name,'a'))

# Let's output this to a csv!
header = ['Benchmark', 'Scheme', 'Paramaters', 'Mean Time']
for i in range(len(compiles) - 1):
    new_header = 'Trial {}'.format(i+1)
    header.append(new_header)

insert_header(header)
insert_row('numpy', numpys)
insert_row('compile', compiles)
insert_row('Python->Weld', encodes)
insert_row('Weld->Python', decodes)
insert_row('Weld', welds)
insert_row('offloaded to numpy',numpy_offloads)
insert_row('Weld end-to-end', weld_totals)
