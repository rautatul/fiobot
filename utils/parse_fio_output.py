from collections import defaultdict
import re

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

