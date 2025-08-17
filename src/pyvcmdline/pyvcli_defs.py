"""
this module contains only declarations, tied to the pyv-cli tool implementation.
"""
from pyved_engine.concr_engin import pe_vars


VER_DISP_MSG = 'Pyved-engine %s  |  github.com/pyved-solution\nAuthors: Thomas I. EDER and others (c) 2018-2024'


def read_ver():
    return pe_vars.ENGINE_VERSION_STR
