# Test configuration
# Syntax: Python

import glob

# The files list is used for all jobs, modified by each job's 'exclude' list if
# available.
files = []
files.extend(glob.glob('*.cnf'))
files.extend(glob.glob('*.smt2'))
files.extend(glob.glob('*.gz'))

common_flags = ['-v']

jobs = [
    {
      'name':    'marco_py', 
      'cmd':     '../marco.py',
      'flags':   ['', '-m', '-M'],
      'flags_all': common_flags,
    },
    {
      'name':    'marco_py', 
      'cmd':     '../marco.py',
      'flags':   ['-b low', '-m -b low', '-M -b low'],
      'flags_all': common_flags,
      'exclude': ['dlx2_aa.cnf'],
    },
]
