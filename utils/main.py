#!/usr/bin/python3

import os
import time
import datetime
import argparse
import subprocess
import re
from collections import defaultdict
from utils.run_nvme import run_nvme
from utils.run_nvme import nvme_detail
from scripts.create_fio_conf import create_fio_conf
from scripts.run_fio_test import run_fio_test
from crontab import CronTab
from scripts.run_night_test import run_night_test
# from utils.check_overlap import check_overlap

if __name__ == "__main__":

    available_disks = run_nvme()
    parser = argparse.ArgumentParser(description='Run fio test.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=str, help='Path to the ini file for FIO test.')
    group.add_argument('-g', '--generate', type=str, help='Set test parameters and generate FIO test script with given name')
    group.add_argument('-t', '--text', type=str, help='Custom fio parameters as text.')
    group.add_argument('-n', '--night', type=str, help='configure night test knob')
    group.add_argument('-d', '--drives', type=str, help='show drive information')
    args = parser.parse_args()
    
    print(args)

    if args.file:
        if not os.path.isfile(args.file):
            parser.print_usage()
            print(f"{args.file} does not exist.")
            exit(1)
        date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        outputfile = "storage/" + str(args.file) + str(date)
        run_fio_test(args.file, outputfile)
    elif args.drives:
        if args.drives == "general":
            print(run_nvme())
        elif args.drives == "detail":
            print(nvme_detail())
    elif args.text:
        date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        test_cond = create_fio_conf(args.text, available_disks)
        outputname = "storage/" + str(date) + str(test_cond)
        print(outputname)
        run_fio_test("fio_config.ini", outputname)
    elif args.generate:
        test_cond = create_fio_conf(args.generate, available_disks)
    elif args.night:
        cron = CronTab(user='root')
        if args.night == "yes":
            with open(f'utils/nightlyflag.txt', 'w') as f:
                f.write("1")
            print("nightly test turned on, don't set a task earlier than 0:30 am")
            for job in cron:
                print(job)
        elif args.night == "no":
            with open(f'utils/nightlyflag.txt', 'w') as f:
                f.write("0")
            print("nightly test turned off")
        elif "insert" in args.night:
            pwd = os.getcwd()
            command_new = "/usr/bin/python3 " + str(pwd) + "/main.py -n \"" + str(args.night[13:]) + "\""
            request_time = str(args.night[7:12]) + "* * *"
            index1 = command_new.find("test_length.")
            index2 = command_new.find(" ", index1)
            if index1 == None:
                print("please specify a test_length")
                exit()
            time = command_new[index1 : index2]
            job = cron.new(command=command_new)
            job.setall(request_time)
            # job.setall('* * * * *')
            cron.write()
        else:
            flag = None
            with open(f'utils/nightlyflag.txt', 'r') as f:
                flag = f.read()
            if flag == "1":
                pwd = os.getcwd()
                for job in cron:
                    if "test_automation_project" in str(job):
                        index1 = str(job).find("python3 ")
                        index2 = str(job).find("/main", index1)
                        pwd = (str(job)[index1+8 : index2])
                        break
                date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
                test_cond = create_fio_conf(args.night, available_disks)
                outputname = pwd + "/nightly/" + str(date) + str(test_cond)
            
                fio_name = pwd + "/fio_config.ini"
                run_night_test(fio_name, outputname)
