#!/usr/bin/env python3
import sys
import csv
import ast


class Result:
    def __init__(self, filename, args, attacks):
        self.filename = filename
        self.args = args
        self.attacks = attacks
        self.pyglaf_time = 0
        self.z3_time = 0
        self.pyglaf_result = []
        self.z3_result = []

    def compare_results(self):
        pass

    def __str__(self):
        return '--------------------' + '\n' + 'Filename ' + str(self.filename) + ', args ' + str(self.args) + ', attacks ' + str(self.attacks) + '\n' + \
            'Pyglaf: ' + str(self.pyglaf_time) + '\n' + \
            'Z3: ' + str(self.z3_time) + '\n' + \
            '----------------------'

            
csv.field_size_limit(sys.maxsize)
f = open('./pyglaf_preferred.csv')
pyglaf = csv.DictReader(f)
z3 = csv.DictReader(open('./20190110_preferred_results.csv'))

my_results = dict()

for row in z3:
    my_results[row['Name']] = Result(row['Name'], row['Args'], row['Attacks'])
    my_results[row['Name']].z3_time = row['Time']
    test = row['Result'].replace(' ', '').replace('[[', '[').replace(']]', ']').replace('],[', '], [').replace("'", '').split(', ')
    for item in test:
        my_results[row['Name']].z3_result.append(item[1:-1].split(','))

for row in pyglaf:
    my_results[row['Name']].pyglaf_time = row['Time']
    s = row['Result'][2:-3]
    strs = s.replace('[[','[').replace(']]',']').split(', ')
    for item in strs:
        my_results[row['Name']].pyglaf_result.append(item[1:-1].split(','))

count = 0
for k, v in my_results.items():
    if v.z3_result == v.pyglaf_result:
        count += 1

print('Correct results: ' + str(count) + '/50')
