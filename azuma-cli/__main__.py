import os
import logging
import argparse

from azuma.exception import *
from azuma import *

parser = argparse.ArgumentParser(description='Azuma CLI - audio distribution tool')

parser.add_argument('command', metavar='command', type=str, nargs='?', help='command to execute')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
args = parser.parse_args()
