#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Script to demonstrate parallel geo query operations

# libraries
import requests, json
from multiprocessing import Pool
from argparse import ArgumentParser


def get_args():
    # parameters: <number of data points> <number of threads>
    argparser = ArgumentParser(description = 'Parallel Geo Query Script')
    argparser.add_argument(
        'datapoints',
        type=int,
        help="Number of data points to sample from spapp DB"
    )
    argparser.add_argument(
        'threads',
        type=int,
        help="Number of threads to run query test with",
        default=8
    )
    myargs = argparser.parse_args()
    
# Obtain a list of specified device check-in points from 'spapp' Cloudant database starting at a random skip value
def get_point_set(pointCount):
    pass


# Record start time and spawn separate tasks
def begin_run(threads):
    pass

# Inside each task:
def query_task():
    pass
    # Perform geofence lookups for each set of coordinates
    
    # Return number of fences found and speed of operation in response
    
    # print results for each thread.
    
def print_results():
    pass
