import os
import time
import datetime
import argparse
import subprocess
import re
from collections import defaultdict
from utils.parse_fio_output import parse_fio_output

def run_fio_test(params, outputname):
    command = f"unbuffer fio {params} > dyoutput.txt"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    outputs = []
    while process.poll() is None:
        pass
    #     output = process.stdout.readline().decode()
    #     if output:
    #         outputs.append(output)
    # for outitms in outputs:
    #     print(outitms)
    time.sleep(1)
    with open('dyoutput.txt', 'r') as file:
        for line in file:
            outputs.append(line)
    if '/' in outputname:
        outputname = outputname.split('/')[-1]
        outputname = "storage/" + outputname
    results = parse_fio_output(''.join(outputs))
    # date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    with open(f'{outputname}.txt', 'w') as f:
        f.write("SUMMARY\n")
        f.write(''.join(outputs))
        f.write("===========================================================\n")
        f.write("SCRIPT:\n")
        with open(f'fio_config.ini', 'r') as f1:
            f1_content= f1.read()
            f.write(f1_content)
    result_value = []
    print("Time (s)\tread MB/s\twrite MB/s\tread IOPS\twrite IOPS")
    for i in range(len(results['read MB/s'])):
        print(f"{i}\t\t{results['read MB/s'][i]}\t\t{results['write MB/s'][i]}\t\t{results['read IOPS'][i]}\t\t{results['write IOPS'][i]}")
        result_value.append(f"{i}\t\t{results['read MB/s'][i]}\t\t{results['write MB/s'][i]}\t\t{results['read IOPS'][i]}\t\t{results['write IOPS'][i]}")

    with open(f'{outputname}.txt', 'a') as f:
        f.write("\n===========================================================\n")
        f.write("RESULTS:\n")
        f.write("Time (s)\tread MB/s\twrite MB/s\tread IOPS\twrite IOPS\n")
        for item in result_value:
            f.write(item)
            f.write("\n")

