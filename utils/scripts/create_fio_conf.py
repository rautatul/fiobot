import collections
import datetime

def create_fio_conf(input_str, available_drives):
    defaults = {
        "drives": 1,
        "test_length": 10,
        "bs_number": None,
        "iodepth": 64,
        "job_number": None,
        "dest": None,
        "select_dr": None,
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

    # print(available_drives)
    if parameters["select_dr"] is not None:
        selected_drives=parameters["select_dr"].split("#")
        available_drives=selected_drives
        parameters["drives"] = len(available_drives)
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
    if parameters["dest"] is not None:
        dest_file = parameters["dest"]
        with open(dest_file, "w") as f:
            f.write(global_config)
            f.write(job_configs)
    else:
        with open("fio_config.ini", "w") as f:
            f.write(global_config)
            f.write(job_configs)
    test_cond = str(parameters["test_format"]) + str(parameters["drives"]) + "-job" +str(parameters["job_number"]) + "-iod" +str(parameters["iodepth"]) + "-bs" +str(parameters["bs_number"])
    print(test_cond)
    return(test_cond)
