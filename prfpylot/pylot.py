from prfpylot.filemover import FileMover
import os
import shutil
import subprocess
import time


class Pylot(FileMover):
    """Start all Profast processes."""

    def __init__(self, input_file):
        super(Pylot, self).__init__(input_file)

    def run(self):
        # run all processes
        # delete temporary files
        pass

    def run_preprocess(self, NumberOfProcesses=1, deleteExistingFolders=True):
        # generate input file:
        self.generate_prf_input("prep")
        # add spectra to this input file.
        self.add_spectra_to_preprocess()
        # start preprocess
        # preprocess needs a 'cal' folder next to the input folder:
        for date in self.dates:
            date_str = date.strftime("%y%m%d")
            igram_folder = os.path.join(self.igram_path, date_str)
            cal_path = os.path.join(igram_folder, 'cal')
            if os.path.exists(cal_path):
                shutil.rmtree(cal_path)
            else:
                os.mkdir(cal_path)

        # Now we can make us ready for finally running preprocess:
        self.prep_path = os.path.join(self.base_path, "prf", "preprocess")
        if NumberOfProcesses == 1:
            preprocess = os.path.join(self.prep_path, "preprocess4.exe")
            # subprocess.Popen(["start", "/wait", "cmd", "/c", preprocess],
            #                  shell=False, cwd=prep_path)
            print("INFO: Starting preprocess4 without parallelisation.")
            p = subprocess.Popen([preprocess],
                                 shell=False, cwd=self.prep_path,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate()
            # TODO: catch if it is not encodable by utf-8
            out = out.decode('utf-8')
            err = err.decode('utf-8')
            if len(err) != 0:
                print('WARNING: Error while running preprocess\n' + err)
            logfile = "LogFilePreprocess_" + self.site_name + '_'\
                      + self.dates[0].strftime('%y%m%d') + '_'\
                      + self.dates[-1].strftime('%y%m%d') + '.txt'
            with open(os.path.join(self.prep4_logpath, logfile), 'w') as f:
                f.write('Output of Preprocess: \n' + out)
                f.write('Error of Preprocess: \n' + err)
        else:
            # TODO: Change this or the single thread method such that only one
            #       version is used.
            preprocess = os.path.join(self.prep_path, "preprocess4.exe {} {}")
            pList = []
            for n in range(NumberOfProcesses):
                pList.append(
                 subprocess.Popen(["start", "/wait", "cmd", "/c",
                                   preprocess.format(NumberOfProcesses, n)
                                   ],
                                  shell=True, cwd=self.prep_path
                                  )
                             )
            # the sleep here is necessary, since the subprocesses are
            # startet without retardation.
            # Hence the loop would be executed before the p's are filled
            # into the list
            time.sleep(0.5)
            for p in pList:
                p.wait()
        # Finally move the files to the spectra folder:
        self.move_bin_files(deleteExistingFolders)

    def run_pcx(self):
        # move bin files with function form FileMover class
        # run pcx.exe
        pass

    def run_inv(self):
        pass
