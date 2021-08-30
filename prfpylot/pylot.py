from prfpylot.filemover import FileMover
from subprocess import Popen, PIPE
import os
import shutil
import time
import sys


class Pylot(FileMover):
    """Start all Profast processes."""

    def __init__(self, input_file):
        super(Pylot, self).__init__(input_file)
        self.logger.debug('Initialized the FileMover')

    def run(self):
        # run all processes
        # delete temporary files
        pass

    def run_preprocess(self, NumberOfProcesses=1, deleteExistingFolders=True):
        self.create_process_log_dir()

        # generate input file:
        self.logger.info("Starting preprocessing ...\n")
        self.logger.info("Generate input file...")
        self.generate_prf_input("prep")
        # start preprocess
        # preprocess needs a 'cal' folder next to the input folder:
        for date in self.dates:
            date_str = date.strftime("%y%m%d")
            igram_folder = os.path.join(self.igram_path, date_str)
            cal_path = os.path.join(igram_folder, 'cal')
            if os.path.exists(cal_path):
                shutil.rmtree(cal_path)
            os.mkdir(cal_path)

        # Now we can make us ready for finally running preprocess:
        prep_path = os.path.join(self.base_path, "prf", "preprocess")

        # Create a logfile for the output of preprocess:
        logfile = "LogFilePreprocess_" + self.site_name + '_'\
                  + self.dates[0].strftime('%y%m%d') + '_'\
                  + self.dates[-1].strftime('%y%m%d') + '.txt'

        # TODO: Change this or the single thread method such that only one
        #       version is used.

        preprocess = os.path.join(prep_path, "preprocess4.exe")
        if sys.platform == "linux":
            preprocess = os.path.join(prep_path, "preprocess4")

        pList = []
        self.logger.info(f"Process the spectra with {NumberOfProcesses}" +
                         " processes in parallel.")
        self.logger.info(f"This will open {NumberOfProcesses} new consoles. " +
                         "Please note that it is normal that nothing" +
                         " is printed")
        # give the user some time to read this message!:
        time.sleep(2)
        for n in range(NumberOfProcesses):
            self.logger.info(f"Start Task {n} of {NumberOfProcesses}")
            pList.append(
             Popen([preprocess, str(NumberOfProcesses), str(n)],
                   shell=False, cwd=prep_path,
                   stdout=PIPE,
                   stderr=PIPE
                   )
                        )
        # the sleep here is necessary, since the subprocesses are
        # startet without retardation.
        # Hence the next loop would be executed before the p's are filled
        # into the list
        time.sleep(2)
        f = open(os.path.join(self.prep4_logpath, logfile), 'w')
        for c, p in enumerate(pList):
            out, err = p.communicate()
            p.wait()
            self.logger.info(f"Finished Task {n} of {NumberOfProcesses}")
            # TODO: catch if it is not encodable by utf-8
            out = out.decode('utf-8')
            err = err.decode('utf-8')
            if len(err) != 0:
                self.logger.error(
                    'Error while running preprocess\n' + err)
            f.write(f'===================== Task {c} =====================\n')
            f.write(f'Output of Preprocess Task {c}: \n' + out)
            f.write(f'Error of Preprocess: Task {c}\n' + err)
            f.write('===================================================\n')
        f.close()
        # Finally move the files to the spectra folder:
        self.move_bin_files(deleteExistingFolders)

    def run_pcxs(self):
        for date in self.dates:
            self.run_pcxs_at(date)

    def run_pcxs_at(self, date):
        self.generate_pt_intraday(date)

        prf_path = os.path.join(self.base_path, "prf")
        pcxs_executable = os.path.join(prf_path, "pcxs10.exe")
        if sys.platform == "linux":
            pcxs_executable = os.path.join(prf_path, "pcxs10")

        self.generate_prf_input("pcxs", date)
        prf_input_path = self.get_prf_input_path("pcxs", date)
        Popen(
            [pcxs_executable, prf_input_path],
            cwd=prf_path,
            stdout=PIPE, stdin=PIPE)

    def run_inv(self):
        pass

    def collate_results(self):
        pass
