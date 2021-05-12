from prfpylot.filemover import FileMover


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

    def run_pcx():
        # move bin files with function form FileMover class
        # run pcx.exe
        pass

    def run_inv():
        pass
