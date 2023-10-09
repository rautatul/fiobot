# fiobot
Fio Bot to test NVMe workload


FIO Test Automation Tool:

Dependencies:
        Python:
                python-crontab (2.7.1+)
        Linux:
                expect-5.45-14.el7_1.x86_64


This tool performs functionalities:
1. auto generate FIO test scripts
2. auto execute existing FIO test scripts
3. auto generate and execute FIO test scripts
4. schedule nightly FIO benchmarking

The regular test results are stored in /storage folder, the nightly test results are stored in /nightly folder.
The test results contain the FIO script being executed, second to second IO readings, and FIO generated test report.

Detailed usage:

1. for executing existing FIO test script:
        python3 main.py -f "<FIO script>"
        <FIO script> can be filename or directory+filename.
        generated benchmarking result will be stored in /storage folder, with format <FIO script name>_<Date>.txt
        example:
                python3 main.py -f "/root/folder1/script1.ini"

2. for checking available nvme drives:
        python3 main.py -d "<general/detail>"
        "general" option gives only drive names, "detail" option gives same output as "nvme -list"
        example:
                python3 main.py -d "detail"

3. for auto generate FIO test script:
        python3 main.py -g "<benchmarking_options> dest=<destination_file>"
        <destination_file> can be a filename or in directory_filename format. If a directory is not provided, it will be generated in current working directory
        <benchmarking_options> includes:
                test_format=rr/rw/sr/sw         this option is mandatory, if not specified, an error will occur
                drives=<int>                    number of drives for benchmarking, default to 1 if not specify
                test_length=<int>               count in seconds, default 10 seconds
                bs_number=<int>                 buffer size, default 4k for random read/write, 128k for sequential read/write
                job_number=<int>                number of jobs for a single benchmarking task, default 4 for random read/write, 1 for sequential read/write
                iodepth=<int>                   iodepth, default 64
                select_dr=<string>              list of selected drives, seperated with "#" sign, for example "/dev/drive1#/dev/drive2#dev/drive3" if this is specified
                                                        option "drives" will be overwritten
        example:
                python3 main.py -g "test_format=rr dest=/root/folder1/script1.ini"

4. for generating and executing an FIO task:
        python3 main.py -t "<benchmarking_options>"
        generated benchmarking result will be stored in /storage folder, with format <Date>_<Details>.txt
        <benchmarking_options> includes:
                test_format=rr/rw/sr/sw         this option is mandatory, if not specified, an error will occur
                drives=<int>                    number of drives for benchmarking, default to 1 if not specify
                test_length=<int>               count in seconds, default 10 seconds
                bs_number=<int>                 buffer size, default 4k for random read/write, 128k for sequential read/write
                job_number=<int>                number of jobs for a single benchmarking task, default 4 for random read/write, 1 for sequential read/write
                iodepth=<int>                   iodepth, default 64
                select_dr=<string>              list of selected drives, seperated with "#" sign, for example "/dev/drive1#/dev/drive2#dev/drive3" if this is specified
                                                        option "drives" will be overwritten
        example:
                python3 main.py -t "test_format=rr"
5. for configuring nightly tests:
        python3 main.py -n "<nightly_test_options>"
        generated benchmarking result will be stored in /nightly folder, with format <Date>_<Details>.txt
        <nightly_test_options> includes:
                "yes"           signal that all the nightly tests should be performed, print all the scheduled nightly tasks
                "no"            signal that all the nightly tests should not be performed
                "insert <minute> <hour> <benchmarking_options>"
                                <minute> range from 0-59
                                <hour> range from 0-23
                                <benchmarking_options> are the same as in 3.
        example:
                python3 main.py -n "yes"
                give signal to the module, allowing night tasks to perform

                python3 main.py -n "insert 15 1 test_format=rr test_length=300"
                the above will schedule a task, everyday 1:15, perform a 300 second random read task with all other options as default

