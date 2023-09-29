import os

def run_nvme():
    output = os.popen('nvme -list').read()
    output_lines = output.splitlines()
    filtered_lines = [line for line in output_lines if "Intel HNA" in line]
    available_disks = []
    for line in filtered_lines:
        available_disks.append(line.split(' ')[0])

    return available_disks

def nvme_detail():
    output = os.popen('nvme -list').read()
    return output
