import os
import sys
import csv
from itertools import islice
from numpy import *

freq = 500 # Hz

def convert(value, typ):
    value = value.replace(",", ".")     # 10,5 s    →   10.5 s
    value = value.replace("k", "000")   # 1k v      →   1000 v
    if "v" in typ:  #nth sample
        return int(value)
    if "s" in typ:  #seconds
        return int(value)*freq
    if "start" in value or "end" in value:
        return value
    return int(value)

def preprocess(entry, shift):
    spoint = entry[0].split(" ")
    epoint = entry[1+shift].split(" ")
    if(len(spoint) > 1): typ = spoint[1]
    else: typ = "vzorek"
    operand = epoint[0]

    return spoint, epoint, typ, operand

def enumerate(spoint, epoint, step, src):
    start = spoint
    slist = []
    elist = []

    while(start < epoint):
        if((start + step) <= epoint):
            slist.append(start)
            elist.append(start + step)
        if((start + step) > epoint):
            slist.append(start)
            elist.append(epoint)
            break
        start += step

    return slist, elist


def parse(entry, src_file):
    pos_shift = 0
    if(len(entry) == 1 and "-" in entry[0]): entry = entry[0].replace("-", " - ").split("-")
    if(len(entry) >= 3 and ">" in entry[2]): pos_shift += 1

    spoint, epoint, typ, operand = preprocess(entry, pos_shift)

    if "start" in spoint: spoint = "0 v".split(" ")
    if "end" in epoint: epoint = (str(sum(1 for line in open(src_file) if line.rstrip())) + " v").split(" ")

    spoint = convert(spoint[0], typ)
    if(len(epoint) <= 2): epoint = convert(epoint[1-pos_shift], typ)
    else: epoint = convert(epoint[1], epoint[2])
    
    if operand == "+": return(spoint, spoint+epoint)
    if operand == "-": return(spoint-epoint, spoint)
    if operand == ".": return(spoint, epoint)
    if operand == "►" or operand == ">":
        step = convert(entry[1].split(" ")[0], entry[1].split(" ")[1])
        return enumerate(spoint, epoint, step, src_file)

    return(spoint, epoint)

def csvreader(src_file, start_points, end_points):
    volts = []
    dataset = []

    with open(src_file, newline='') as csvfile:
        content = islice(csv.reader(csvfile, delimiter=','), 7, None, None) # Skip the header of length of 7 lines
        for row in content:
            volts.append(int(row[6]))
    
    for start, end in zip(start_points, end_points):
        dataset.append(volts[start:end])
    
    return dataset

def pointReader(point_file):
    src_file = None
    start_points = []
    end_points = [] 
    dataset = []

    all_spoint = []
    all_epoint = []

    file_sep = [0]

    print("Turning pointer list into dataset...")

    with open(point_file) as pfile:
        points = csv.reader(pfile, delimiter="\t")
        for entry in points:
            if entry[0].startswith('#'): continue                   # handle user notes or range (row) disable
            if entry[0].startswith('['):
                if not src_file: src_file = entry[0].split('"')[1]
                else:
                    dataset.extend(csvreader(src_file, start_points, end_points))
                    file_sep.append(len(start_points))
                    all_spoint.extend(start_points)
                    all_epoint.extend(end_points)
                    start_points = []
                    end_points = []
                    src_file = entry[0].split('"')[1]
                continue
            spoint, epoint = parse(entry, src_file)

            if isinstance(spoint, list):
                start_points.extend(spoint)
                end_points.extend(epoint)
            else:
                start_points.append(spoint)
                end_points.append(epoint)

        all_spoint.extend(start_points)
        all_epoint.extend(end_points)
        dataset.extend(csvreader(src_file, start_points, end_points))
        return dataset, start_points, end_points, all_spoint, all_epoint, file_sep

def save(dataset, label):
    num = 0
    for sample in dataset:
        expected_value = mean(sample)
        time = 0.000
        filename = "./dataset/" + label + "/sample_" + str(num) + ".csv"
        print("Writing " + filename + "...")
        with open(filename, 'w') as output:
            for volt in sample:
                output.write(str(format(time, '.3f')) + "\t" + str(round(volt-expected_value, 3)) + "\n")
                time += 1/freq
        num += 1

def main():
        if len(sys.argv) <= 1:
            print("Usage: {0} [dataset pointers directory]".format(sys.argv[0]))
            return
        
        inDIR     = sys.argv[1]

        for root, dirs, files in os.walk(inDIR): 
            for file in files:
                label = os.path.splitext(file)[0]
                dataset = pointReader(os.path.join(root, file))
                save(dataset, label)


if __name__ == '__main__':
    main()