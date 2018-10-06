import os
import logging
import numpy as np
import time
from functools import wraps
import argparse
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up a parser for the keyword arguments
parser = argparse.ArgumentParser()
parser.add_argument('--decorator')
parser.add_argument('--applywraps')
args = parser.parse_args()

# user input decorator and applywrap arguments
# NOTE: We need to eval the applywraps as user-input is always parsed as string
decorator = args.decorator
applywraps = eval(args.applywraps)

# Define the valid options for the arguments
valid_options = {'decorator': ['log', 'time', 'time-log', 'log-time'],
                 'applywraps': [True, False] }

# The error message for each argument type
err_msg = lambda arg:f'Invalid --{arg} argument! '\
                    +f'Valid arguments are:\n {valid_options[arg]}'

# We need to output an error for each wrong argument passed
# TODO||OPTIMIZE: Implement some alternative where if any of the condition is met
#                 a task is run at the END of the loop.
err_stat = False
for arg, opts in valid_options.items():
    argval = eval(arg)
    if (argval not in opts
    or
    (arg is 'applywraps' and type(argval) is not bool)):

        print(err_msg(arg))
        err_stat = True

# Exit if the error is encoutered i.e. a wrong argument is given for either.
if err_stat:
    sys.exit()

out_dir = 'output/logging' # Output directory for logging files
if not os.path.exists(out_dir): # Make it if it doesn't exit.
    os.makedirs(out_dir) # Try and except could work as well.

# Removing the old logging file(s) if they exist for greet and wrapper.
# NOTE: Important to check if it doesn't exist. (Try and except)
remove_file = lambda file: os.remove(file) if os.path.exists(file) else None
funcs = ['greet', 'wrapper']

# HACK: use os.path.join even when we have multiple slashes (leading and trailing)
for func in funcs:
    remove_file(os.path.join(out_dir, f'{func}.log'))

# If user wants to applywraps (preserving orig_func)
if applywraps:
    def my_logger(orig_func):
        logfile = f'output/logging/{orig_func.__name__}.log'
        logging.basicConfig(filename=logfile,   # config for the logger
                            level=logging.INFO)

        @wraps(orig_func)    # wraps preserves the orig_func attr like __name__
        def wrapper(*args, **kwargs):
            logging.info(f'{orig_func.__name__} '+      # log before
            f'ran with args {args} and kwargs {kwargs}')
            return orig_func(*args, **kwargs)           # Then return

        return wrapper # Finally return the wrappper but wrapper.__name__ = 'greet'

# SAME for my_timer
# QUESTION || TODO: Could DRY be implemented in this? (w/o wraps and w wraps)
    def my_timer(orig_func):

        @wraps(orig_func)
        def wrapper(*args, **kwargs):
            t1 = time.time()
            result = orig_func(*args, **kwargs)
            t2 = time.time()
            print(f'The function {orig_func.__name__} ran in {np.round(t2-t1, 5)}s')

        return wrapper
else:
    def my_logger(orig_func):
        logging.basicConfig(filename=f'output/logging/{orig_func.__name__}.log', level=logging.INFO)

        def wrapper(*args, **kwargs):
            logging.info(f'{orig_func.__name__} ran with args {args} and kwargs {kwargs}')
            return orig_func(*args, **kwargs)

        return wrapper


    def my_timer(orig_func):

        def wrapper(*args, **kwargs):
            t1 = time.time()
            result = orig_func(*args, **kwargs)
            t2 = time.time()
            print(f'The function {orig_func.__name__}',
                  f'ran in {np.round(t2-t1, 5)}s')

        return wrapper


if decorator == 'log':
    @my_logger
    def greet(name, timeofday):
        time.sleep(1)
        print(f'How are you this {timeofday}, {name}?')

elif decorator == 'time':
    @my_timer
    def greet(name, timeofday):
        time.sleep(1)
        print(f'How are you this {timeofday}, {name}?')

elif decorator == 'log-time':
    @my_logger
    @my_timer
    def greet(name, timeofday):
        time.sleep(1)
        print(f'How are you this {timeofday}, {name}?')

elif decorator == 'time-log':
    @my_timer
    @my_logger
    def greet(name, timeofday):
        time.sleep(1)
        print(f'How are you this {timeofday}, {name}?')


greet('Abhi', 'morning')
greet('Abhi', 'evening')
