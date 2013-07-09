import re
import os
import tempfile
import subprocess
import array
import atexit
from MinisatSubsetSolver import MinisatSubsetSolver

class MUSerSubsetSolver(MinisatSubsetSolver):
    def __init__(self, filename):
        MinisatSubsetSolver.__init__(self, filename, store_dimacs=True)
        self.core_pattern = re.compile(r'^v [\d ]+$', re.MULTILINE)
        self.muser_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'muser2-static')
        if not os.path.isfile(self.muser_path):
            raise Exception("MUSer2 binary not found at %s" % self.muser_path)
        try:
            # a bit of a hack to check whether we can really run it
            DEVNULL = open(os.devnull, 'wb')
            p = subprocess.Popen([self.muser_path], stdout=DEVNULL, stderr=DEVNULL)
        except:
            raise Exception("MUSer2 binary %s is not executable.\nIt may be compiled for a different platform." % self.muser_path)

        self._proc = None  # track the MUSer process
        atexit.register(self.cleanup)

    # kill MUSer process if still running when we exit (e.g. due to a timeout)
    def cleanup(self):
        if self._proc:
            self._proc.kill()

    # override shrink method to use MUSer2
    # NOTE: seed must be indexed (i.e., not a set)
    def shrink(self, seed):
        seed = [x for x in seed if x not in self.hard_clauses]  # XXX: Hack.  Best to just make seeds not include hard clauses ever

        # Open tmpfile
        with tempfile.NamedTemporaryFile('wb') as cnf:
            # Write CNF (grouped, with hard clauses, if any, in the 0 / D / Don't-care group)
            header = "p gcnf %d %d %d\n" % (self.nvars, len(seed), len(seed))
            cnf.write(header.encode())
            for i in self.hard_clauses:
                cnf.write("{0} " + self.dimacs[i])  # {0} = D = "Don't care" group -- dimacs[i] has newline
            k = 1
            for i in seed:
                cnf.write(("{%d} " % k) + self.dimacs[i])  # dimacs[i] has newline
                k += 1

            cnf.flush()
            # Run MUSer
            self._proc = subprocess.Popen([self.muser_path, '-comp', '-grp', '-v', '-1', cnf.name],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = self._proc.communicate()
            self._proc = None  # clear it when we're done (so cleanup won't try to kill it)
            out = out.decode()

        # Parse result, return the core
        matchline = re.search(self.core_pattern, out).group(0)
        return array.array('i', (seed[int(x)-1] for x in matchline.split()[1:-1]) )

