#!/usr/bin/env python3
import signal
import sys
import time
from os import listdir
import alias
import subprocess
import json

path = '/home/szczocik/Workspaces/BenchmarkFiles/A/1/'
test = []
# for f in listdir(path):
#     test.append(f)

files = []

with open('/home/szczocik/Workspaces/alias/preferredBenchmarkFiles.json', 'r') as file:
    files = json.load(file)
    # json.dump(test, file)
count = 0


def signal_handler(signum, frame):
    raise Exception("Timed out!")


def write_to_file(text):
    with open('/home/szczocik/Workspaces/alias/results/20190110_preferred_results.csv', 'a') as file:
        file.write(text)


def run_test(filename):
    print('Reading file')
    start_r = time.time()
    af = alias.read_tgf(filename)
    end_r = time.time()
    print('Finished reading file')
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(1200)

    print('Start computing stable extension')
    start = time.time()
    try:
        stable = af.get_stable_extension()
        end = time.time()
        print('End computing stable extension')
        print('starting writing to file')
        write_to_file(filename + ';' + str(af.get_args_count()) + ';' + str(af.get_attacks_count()) + ';' + str(end_r - start_r) + ';' + str(end - start) + ';' + str(stable) + '\n')
        print('finished writing to file')
    except Exception as e:
        end = time.time()
        stable = e
        print('End computing stable extension')
        print('starting writing to file')
        write_to_file(filename + ';' + str(af.get_args_count()) + ';' + str(af.get_attacks_count()) + ';' + str(end_r - start_r) + ';' + str(end - start) + ';' + str(stable) + '\n')
    print('finished writing to file')


for item in files:
    count += 1
    print('\n----------------------------\n')
    print('Processing file: ' + str(count) + '/' + str(len(files)))
    print(item)
    run_test(path + item)
