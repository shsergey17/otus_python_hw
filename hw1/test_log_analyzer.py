#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import log_analyzer

class TestMethods(unittest.TestCase):

    def test_get_last_logfile(self):
        filename = os.path.join("./", "test-20170601")
        with open(filename, "w", buffering=-1) as file:
            file.write("test")
        self.assertEqual(log_analyzer.get_last_logfile("./"), ['2017-06-01', './test-20170601'])
        os.remove(filename)

    def test_get_stat(self):
        lines = [['test', 1]]
        ok = [{'count': 1, 'time_avg': 1.0, 'time_max': 1.0, 'time_sum': 1.0, 'url': 'test', 'time_med': 1.0,
        'time_perc': 100.0, 'percent': 100.0}]
        self.assertEqual(log_analyzer.get_stat(lines), ok)

    def test_median(self):
        self.assertEqual(log_analyzer.median([1,2,3,4,5,6]), 3.5)

    def test_process_line(self):
        text = """1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25047606 HTTP/1.1" 200 959 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752766" "dc7161be3" 2.490"""
        self.assertEqual(log_analyzer.process_line(text), ['/api/v2/banner/25047606', '2.490'])

    def test_xreadlines(self):
        filename = os.path.join("./", "test-20170601")
        text = """1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25047606 HTTP/1.1" 200 959 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752766" "dc7161be3" 2.490"""
        with open(filename, "w", buffering=-1) as file:
            file.write(text)

        for a in log_analyzer.xreadlines(filename):
            res = a
        self.assertEqual(res, ['/api/v2/banner/25047606', '2.490'])
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()