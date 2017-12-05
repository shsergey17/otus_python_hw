import os
import re
import stat
from collections import namedtuple
import datetime
# folder = "./log"
# files = (os.path.join(folder, name) for name in os.listdir(folder))
# entries = ((path, os.lstat(path)) for path in files)  # don't follow symlinks
# path, _ = max((e for e in entries if stat.S_ISREG(e[1].st_mode)),  # find regular files
#               key=lambda e: getattr(e[1], 'st_birthtime', None) or e[1].st_ctime)
# print(path)

# tree = os.walk('./test')
# for d, dirs, files in tree:
#     print files
#
#
#
# a = [files for d, dirs, files in tree]


logs = [re.findall('nginx-access-ui\.log-(\d{8})[\.gz]*', logfile) for logfile in os.listdir('./test')]
logs = [logfile for logfile in os.listdir('./test')]
# print logs
# max_date = max([re.findall('./', log) for log in logs])[0]


logs=[
    'nginx-access-ui-bad.log-20170731.gz',
'nginx-access-ui-bad.log-2017.gz',
'nginx-access-ui-bad.log-201707.gz',
'nginx-access-ui-bad.log-20170731.gz',
'nginx-access-ui-bad.log-20170728.gz',
'nginx-access-ui-bad.log-20170729.gz',
'nginx-access-ui-bad.log-20170730.gz','asd'
]

# logs = [os.path.join(log_path, logfile) for logfile in os.listdir(log_path)]
# max_date = max([re.findall(pattern, log) for log in logs])[0]
# for log in logs:
#     matches = re.findall(pattern, log)
#     if matches:
#         if matches[0] == max_date:
#             Log = namedtuple('Log', ['maxdate', 'logfile'])
#             return Log(str(datetime.datetime.strptime(max_date, "%Y%m%d").date()), log)

def get_file():
    try:
        for line in logs:
            parsed_line = re.findall('nginx-access-ui-bad\.log-(\d{8})[\.gz]*', line)
            if parsed_line:
                yield parsed_line
    except IOError, e:
        raise Exception("%s: %s" % (e, log_path))

# for a in get_file():
#     print a
#
Log = namedtuple('Log', ['maxdate', 'logfile'])

def gets():
    max_date = 0
    file = ''
    for logfile in os.listdir("./log"):

        find = re.search('nginx-access-ui\.log-(\d{8})[\.gz]*', logfile)
        return find.start()
        if find and max_date < find:
            max_date, file = find[0], logfile

    if max_date:
        max_date = str(datetime.datetime.strptime(max_date, "%Y%m%d").date())
    return Log(max_date, file)

print gets()
