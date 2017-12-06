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
            elif 'bohrium took' in line and time:
                assert numpy_total == 0
                numpy_total = time
        print('********************************************')

    print('Numpy: ', numpy_total)
    numpys.append(numpy_total)
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

print('num trials = ', len(numpys))

numpys.insert(0, float(sum(numpys)) / len(numpys))

# CSV dump time!
name = args.file + '.csv'
file_name = os.path.join(args.dir, name)
dumpster = csv.writer(open(file_name,'a'))

# Let's output this to a csv!
header = ['Benchmark', 'Scheme', 'Paramaters', 'Mean']
for i in range(len(compiles) - 1):
    new_header = 'Trial {}'.format(i)
    header.append(new_header)

insert_header(header)
insert_row('numpy', numpys)
