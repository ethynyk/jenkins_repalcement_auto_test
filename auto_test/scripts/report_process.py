import re
import sys
import os
import logging


def report_processing(report, out_file):
    info_regex = re.compile(r'(\d{4}(?:-\d{2}){2})\s(\d{2}(?::\d{2}){2})\s(INFO)')
    info_sub = r'\1 \2 &lt;span class=\&#34;log-info\&#34;&gt;INFO&lt;/span&gt;'
    warning_regex = re.compile(r'(\d{4}(?:-\d{2}){2})\s(\d{2}(?::\d{2}){2})\s(WARNING)')
    warning_sub = r'\1 \2 &lt;span class=\&#34;log-warning\&#34;&gt;WARNING&lt;/span&gt;'
    error_regex = re.compile(r'(\d{4}(?:-\d{2}){2})\s(\d{2}(?::\d{2}){2})\s(ERROR)')
    error_sub = r'\1 \2 &lt;span class=\&#34;log-error\&#34;&gt;ERROR&lt;/span&gt;'

    if not os.path.isfile(report):
        logging.error('{} is not a file'.format(report))
        return

    with open(out_file, 'w', encoding='utf-8') as w:
        with open(report, 'r', encoding='utf-8') as r:
            for line in r:
                line = info_regex.sub(info_sub, line)
                line = warning_regex.sub(warning_sub, line)
                line = error_regex.sub(error_sub, line)
                w.write(line)


if __name__ == "__main__":
    in_report = sys.argv[1]
    out_report = sys.argv[2]
    report_processing(in_report, out_report)
