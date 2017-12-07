#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import gzip
import datetime
import json
import argparse
from itertools import groupby
import os.path
import logging
import time
from collections import namedtuple
import shutil
import codecs


# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


LINE_REGEXP = re.compile(r"\"\S+ (\S+) \S+\" .+ (\S+)")

config = {
    # Размер отчета
    "REPORT_SIZE": 1000,

    # Путь к папке с отчетами
    "REPORT_DIR": "./reports",

    # Путь к папке с логами
    "LOG_DIR": "./log",

    # ts-file
    "TS": "./log_analyzer.ts",

    # шаблон для поиска логов
    "LOG_TEMPLATE": "nginx-access-ui\.log-(\d{8})[\.gz]*",

    # лог файл скрипта
    "APP_LOG_FILE": "",

    # Ошибка при привышении ошибочных строк в логе, в процентах
    "LOG_ERROR_THRESHOLD_PERCENT": 50
}


def xreadlines(log_path):
    """
    Чтение файла
    :param log_path: лог
    :return: iterator
    """
    try:
        if log_path.endswith(".gz"):
            log = gzip.open(log_path, 'rb')
        else:
            log = codecs.open(log_path, 'rt', encoding="utf-8")
        total = processed = 0
        for line in log:
            # .decode("utf-8", "replace"
            parsed_line = process_line(line)
            total += 1
            if parsed_line:
                processed += 1
                yield parsed_line

        logging.info("%s of %s lines processed" % (processed, total))
        log.close()

        percent = round((total - processed) * 100 / total)
        if percent > config['LOG_ERROR_THRESHOLD_PERCENT']:
            raise Exception('Bug threshold exceeded %d of %d' % (percent, config["LOG_ERROR_THRESHOLD_PERCENT"]))

    except IOError, e:
        raise Exception("%s: %s" % (e, log_path))


def process_line(line):
    """
    Поиск
    :param line: list
    :return: list
    """
    matches = re.search(LINE_REGEXP, line)
    if matches:
        return [matches.group(1), matches.group(2)]


def median(lists):
    """
    Медиана
    :param lists: list
    :return: float
    """
    median = 0
    sortedlist = sorted(lists)
    lengthofthelist = len(sortedlist)
    centerofthelist = lengthofthelist / 2
    if len(sortedlist) % 2 == 0:
        temp = 0.0
        medianparties = sortedlist[centerofthelist - 1: centerofthelist + 1]
        for value in medianparties:
            temp += value
            median = temp / 2
        return median
    else:
        return sortedlist[centerofthelist]


def save_report(report_path, template, stat_result):
    """
    :param report_path: str путь к папке отчетов
    :param template: шаблон
    :param stat_result: dict статистика
    :return: void
    """
    try:

        with open(template) as file:
            text = file.read()
        text = text.replace('$table_json', json.dumps(stat_result))

        tmp_report = report_path + '.tmp'

        with codecs.open(tmp_report, "wt", encoding="utf-8") as file:
            file.write(text)

        shutil.move(tmp_report, report_path)

        return True

    except OSError, e:
        raise Exception("%s: %s" % (e, report_path))


def get_stat(log_lines):
    """
    Генерация статистики
    :param log_lines: list
    :return: list
    """
    total_request = 0
    group = []
    for url, request_times in groupby(sorted(log_lines, key=lambda x: x[0]), key=lambda x: x[0]):
        times = []
        result = {}
        for c, request_time in request_times:
            times.append(float(request_time))
            result['url'] = url
            result['request'] = times
            total_request += float(request_time)
        group.append(result)

    stat_result = []
    total = len(group)
    # logging.debug("total: %d, total_request: %f" % (total, total_request))
    for item in group:
        item_request = item['request']
        stat_result.append({
            'count': len(item_request),
            'time_avg': round(sum(item_request) / len(item_request), 3),
            'time_max': max(item_request),
            'time_sum': round(sum(item_request), 3),
            # 'url': item['url'].decode("utf-8", "replace").encode("utf-8"),
            'url': item['url'],
            'time_med': round(median(item_request), 3),
            'time_perc': round(100 * sum(item_request) / float(total_request), 3),
            'percent': round(100 * len(item_request) / float(total), 3),
        })
    return sorted(stat_result, key=lambda r: r["time_sum"], reverse=True)[:config["REPORT_SIZE"]]


def get_last_logfile(log_path):
    """
    Поиска лог файла и максимальной даты
    :param log_path:  путь к логам
    :return: Log [макс дата, логфайл]
    """
    try:
        pattern = re.compile(config["LOG_TEMPLATE"])
        if not os.path.isdir(log_path):
            logging.info("%s: %s" % ("Not found", log_path))
            sys.exit(0)

        Log = namedtuple('Log', ['maxdate', 'logfile'])
        max_date = 0
        findfile = ''
        for logfile in os.listdir(log_path):
            find = re.findall(pattern, logfile)
            if find and max_date < find:
                max_date, findfile = find[0], os.path.join(log_path, logfile)

        if max_date:
            max_date = str(datetime.datetime.strptime(max_date, "%Y%m%d").date())
        else:
            logging.info("%s: %s" % ("File not found", log_path))
            sys.exit(0)

        return Log(max_date, findfile)

    except OSError, e:
        raise Exception("%s: %s" % (e, log_path))


def create_ts(ts_file):
    """
    Создание ts file
    :param ts_file:
    :return: void
    """
    if config["TS"]:
        with open(ts_file, 'w') as file:
            file.write(str("%d" % time.time()))


def getopt():
    """
    Аргументы к скрипту
    :return: args
    """
    parser = argparse.ArgumentParser("Process log files")
    parser.add_argument("--config",
                        dest="config",
                        default="./log_analyzer.conf",
                        help="Config file")
    return parser.parse_args()


def main(config):
    Log = get_last_logfile(config["LOG_DIR"])

    logging.info("date: %s, logfile: %s" % (Log.maxdate, Log.logfile))

    report_file = os.path.join(config["REPORT_DIR"], "report-%s.html" % Log.maxdate)
    if os.path.isfile(report_file):
        logging.info("%s: %s" % ("Report file already exists", report_file))
        return

    # Чтение файла
    log_lines = xreadlines(Log.logfile)

    # Получение статистики
    stat_result = get_stat(log_lines)

    # Загрузка шаблона
    template = os.path.join(config["REPORT_DIR"], "report.html")

    # Генерация отчета
    if save_report(report_file, template, stat_result):
        logging.info("Create report %s" % report_file)
    create_ts(config["TS"])


def readconf(filename):
    """
    Чтение конфигурации
    :param filename:
    :return: config
    """
    try:
        with open(filename, 'r') as file:
            config.update(json.loads(file.read()))

        return config

    except OSError, e:
        raise Exception("%s: %s" % (e, filename))


if __name__ == "__main__":
    """
        python log_analyzer.py
        
        python log_analyzer.py --config=config.cfg
        
        python -m unittest discover -p test_log_analyzer.py
    """
    args = getopt()
    params = {
        'format': u'[%(asctime)s] %(levelname)-8s %(message)s',
        'level': logging.INFO
    }

    config = readconf(args.config)

    if config["APP_LOG_FILE"]:
        params['filename'] = config["APP_LOG_FILE"]

    logging.basicConfig(**params)

    try:
        main(config)

    except Warning as e:
        logging.info(e)
    except Exception as e:
        logging.exception(e)
