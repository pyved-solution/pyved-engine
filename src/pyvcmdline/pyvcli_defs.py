"""
this module contains only declarations, tied to the pyv-cli tool implementation.
"""
from pyved_engine.concr_engin import pe_vars


MAIN_AUTH = 'Thomas IWASZKO EDER'
cYEAR = '2025'
VER_DISP_MSG = (
    "\npyved-engine version %s\n"
    f"© 2018–{cYEAR} {MAIN_AUTH} and contributors.\n\n"
    "Project___ https://github.com/pyved-solution/pyved-engine\n"
    "Issues____ https://github.com/pyved-solution/pyved-engine/issues\n"
    "License___ LGPL-3.0\n"
)


def read_ver():
    return pe_vars.ENGINE_VERSION_STR
