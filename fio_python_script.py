import os
import time
import datetime
import argparse
import subprocess
import re
from collections import defaultdict


def run_nvme():
    output = os.popen('nvme -list').read()
    output_lines = output.splitlines()
    filtered_lines = [line for line in output_lines if "Intel HNA" in line]
    available_disks = []
    for line in filtered_lines:
        available_disks.append(line.split(' ')[0])

    return available_disks
    
def create_fio_conf(input_str, available_drives):
    defaults = {
        "drives": 1,
        "test_length": 10,
        "bs_number": None,
        "iodepth": 64,
        "job_number": None,
    }
    test_format_mapping = {
        "rr": "randread",
        "rw": "randwrite",
        "sr": "read",
        "sw": "write",
    }

    parameters = {key: value for key, value in (part.split("=") for part in input_str.split())}

    if "test_format" not in parameters:
        raise ValueError("test_format is required")

    for key, default in defaults.items():
        parameters.setdefault(key,default)

    if parameters["bs_number"] is None:
        parameters["bs_number"] = 4 if parameters["test_format"] in {"rr", "rw"} else 128

    if parameters["job_number"] is None:
        parameters["job_number"] = 4 if parameters["test_format"] in {"rr", "rw"} else 1

    parameters["test_format"] = test_format_mapping[parameters["test_format"]]

    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    global_config = f"""
[global]
name={parameters['drives']}drive_{parameters['test_format']}_{parameters['test_length']}_{date_time_str}
ioengine=libaio
direct=1
bs={parameters['bs_number']}k,{parameters['bs_number']}k
rw={parameters['test_format']}
iodepth={parameters['iodepth']}
numjobs={parameters['job_number']}
buffered=0
size=100%
runtime={parameters['test_length']}
time_based
randrepeat=0
norandommap
refill_buffers
    """    
    job_configs = "\n".join(
        f"""
        [job{i+1}]
        filename={drive}
        """
        for i, drive in enumerate(available_drives[:int(parameters["drives"])])
    )
    with open("fio_config.ini", "w") as f:
        f.write(global_config)
        f.write(job_configs)

def parse_fio_output(output):
    results = defaultdict(list)
    pattern = re.compile(r'\[r=(.*?iB/s),w=(.*?iB/s)\]\[r=(.*?),w=(.*?) IOPS\]')
    for line in output.split('\n'):
        match = pattern.search(line)
        if match:
            results['read MB/s'].append(match.group(1)[:-5])
            results['read IOPS'].append(match.group(3))
            results['write MB/s'].append(match.group(2)[:-5])
            results['write IOPS'].append(match.group(4))
    return results

def run_fio_test(params):
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
 
    results = parse_fio_output(''.join(outputs))
    date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    with open(f'fio_test_on_{date}.txt', 'w') as f:
        f.write(''.join(outputs))

    print("Time (s)\tread MB/s\twrite MB/s\tread IOPS\twrite IOPS")
    for i in range(len(results['read MB/s'])):
        print(f"{i}\t\t{results['read MB/s'][i]}\t\t{results['write MB/s'][i]}\t\t{results['read IOPS'][i]}\t\t{results['write IOPS'][i]}")

if __name__ == "__main__":

    available_disks = run_nvme()
    parser = argparse.ArgumentParser(description='Run fio test.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=str, help='Path to the ini file for fio test.')
    group.add_argument('-t', '--text', type=str, help='Custom fio parameters as text.')

    args = parser.parse_args()

    if args.file:
        if not os.path.isfile(args.file):
            parser.print_usage()
            print(f"{args.file} does not exist.")
            exit(1)
        run_fio_test(args.file)
    elif args.text:
        create_fio_conf(args.text, available_disks)
        run_fio_test("fio_config.ini")
