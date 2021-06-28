from prfpylot.filemover import FileMover
import subprocess


class Pylot(FileMover):
    """Start all Profast processes."""

    def __init__(self, input_file):
        super(Pylot, self).__init__(input_file)

    def run():
        # run all processes
        # delete temporary files
        pass

    def run_preprocess():
        # get parameters and generate Template file
        # start preprocess
        pass

    def run_pcx(self):
        for date in self.dates:
            self.run_pcx_at(date)

    def run_pcx_at(self, date):
        self.generate_prf_input("pcxs", date)
        subprocess.run(["./pcxs10", "pcxs10.inp"])

    def run_inv():
        pass
