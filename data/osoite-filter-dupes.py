#!/usr/bin/env python
import os
import csv
import sys

def filter_dupes():
    reader = csv.reader(sys.stdin, delimiter=',')
    writer = csv.writer(sys.stdout, delimiter=',')
    reader.next()
    addr_hash = {}
    for idx, row in enumerate(reader):
        if not row[-1]:
            s = "%s %s, %s" % (row[0], row[1], row[10])
            sys.stderr.write("No type found: %s\n" % s)
            continue
        row_type = int(row[-1])
        if row_type != 1:
            continue
        street = row[0]
        if not row[1]:
            continue
        num = int(row[1])
        if not num:
            continue
        num2 = row[2]
        if not num2:
            num2 = None
        letter = row[3]
        muni_name = row[10]
        coord_n = int(row[8])
        coord_e = int(row[9])
        e = (muni_name, num, num2, letter)
        if street in addr_hash:
            if num2 == None:
                num2s = ''
            else:
                num2s = str(num2)
            found_dupe = False
            for s in addr_hash[street]:
                if s == e:
                    sys.stderr.write("Dupe: %s,%d,%s,%s,%s\n" % (street, num, num2s, letter, muni_name))
                    found_dupe = True
                    break
            else:
                addr_hash[street].append(e)
            if found_dupe:
                continue
        else:
            addr_hash[street] = [e]
        writer.writerow(row)

filter_dupes()
