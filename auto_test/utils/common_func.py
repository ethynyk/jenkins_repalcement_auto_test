import re
from datetime import datetime
import inspect
import logging


def init_logging(script_name):
    """
    Init logging format
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("auto_test.log"),
                  logging.StreamHandler()],
    )
    logger = logging.getLogger(script_name)
    return logger


def print_function():
    """
    Print function
    """
    caller_function_name = inspect.currentframe().f_back.f_code.co_name
    print(f"[Run {caller_function_name} function]")


def extract_time(time_str, time_format="%a %b %d %H:%M:%S %Y"):
    """
    Extranct formatted time from str

    :param time_format:
        time_format = "%a %b %d %H:%M:%S %Y"
    """
    # print(f"Debug: time_str={time_str}\n time_str2={time_str2}")
    time_pattern = re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) \b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \b\d{1,2} \d{1,2}:\d{2}:\d{2} [A-Z]{3} \d{4}\b')
    # Use regular expressions to find the time string
    time_match = time_pattern.search(time_str)
    # If no matching time string is found, it can't be compared
    if not time_match:
        raise ValueError("No matching time string in the input.")

    # Extract the time string from time_match
    extracted_time = time_match.group()
    extracted_list = extracted_time.split()
    time = ' '.join(extracted_list[:-2] + [extracted_list[-1]])
    # Parse time string
    time_obj = datetime.strptime(time, time_format)
    return time_obj


def is_same_day(time_str1, time_str2):
    """
    Check whether time_str1 and time_str2 is the same day
    """
    # Define time format, including time zones.
    # %Z only support the standard time zone UTC, removing manually.

    time_format1 = "%a %b %d %H:%M:%S %Y"
    date_format2 = "%Y%m%d"
    # Parse time string
    time_obj1 = extract_time(time_str=time_str1, time_format=time_format1)
    time_obj2 = datetime.strptime(time_str2, date_format2)
    # Compare whether the data parts are the same
    print(f"Debug: time_obj1={time_obj1.date()}")
    print(f"Debug: time_obj2={time_obj2.date()}")
    return time_obj1.date() == time_obj2.date()
