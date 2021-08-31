from prfpylot.filemover import FileMover
from subprocess import Popen, PIPE
import os
import shutil
import time
import sys
import glob


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
        # trying to work directly in prfpylot/data:
        # self.move_bin_files(deleteExistingFolders)

    def run_pcxs(self):
        for date in self.dates:
            self.run_pcxs_at(date)

    def run_inv(self):
        for date in self.dates:
            self.run_inv_at(date)

    def run_pcxs_at(self, date):
        prf_path = os.path.join(self.base_path, "prf")
        pcxs_executable = os.path.join(prf_path, "pcxs10.exe")
        if sys.platform == "linux":
            pcxs_executable = os.path.join(
                prf_path, "pcxs10")

        self.generate_prf_input("pcxs", date)
        prf_input_path = os.path.basename(
            self.get_prf_input_path("pcxs", date))

        p = Popen(
            [pcxs_executable, prf_input_path],
            cwd=prf_path)
        out, err = p.communicate()
        p.wait()
        print(out)
        print(err)

    def run_inv_at(self, date):
        self.generate_pt_intraday(date)
        self.generate_prf_input("inv", date)

        prf_path = os.path.join(self.base_path, "prf")
        inv_executable = os.path.join(prf_path, "invers10.exe")
        if sys.platform == "linux":
            inv_executable = os.path.join(
                prf_path, "invers10")
        prf_input_path = os.path.basename(
            self.get_prf_input_path("inv", date))

        p = Popen(
            [inv_executable, prf_input_path],
            cwd=prf_path)
        p.wait()

    def move_result_files(self):
        """
        Move the results to the data folder.
        If the datafolder does exists, the existing folder is renamed adding
        backupX where X increases if an other backup does already exists.
        After renaming, a new folder is created.
        """

        # check if result folder exist already, if not create
        startDate_strng = self.dates[0].strftime("%y%m%d")
        endDate_strng = self.dates[-1].strftime("%y%m%d")
        result_folder = os.path.join(self.results_path,
                                     f"{startDate_strng}_{endDate_strng}"
                                     )
        if os.path.exists(result_folder):
            # check if already other backuped folder exist as well:
            backuped_results = glob.glob(result_folder + "_backup*")
            # rename existing folder by adding _backupN where N is the N-th
            # backup
            result_folder_backup = result_folder\
                + f"_backup{len(backuped_results)}"
            self.logger.warning(f"Result directory {result_folder} exists!" +
                                "Renamed existing one to "
                                f"{result_folder_backup} and create a new one")
            # rename and create new, empty folder
            os.rename(result_folder, result_folder_backup)
            os.makedirs(result_folder)
        else:
            os.makedirs(result_folder)
        # move result files to directory
        # files can be devided in suffix and preafix, where the suffix is
        # constant allt the time:
        suffix_list = ["colsens.dat", "invparms.dat", "job01.spc", "job02.spc",
                       "job03.spc", "job04.spc", "job05.spc"]
        source_folder = os.path.join(self.base_path, "prf", "out_fast")
        for date in self.dates:
            datestr = date.strftime("%y%m%d")
            praefix = self.site_name + datestr + "-"
            for suffix in suffix_list:
                file = praefix + suffix
                shutil.move(os.path.join(source_folder, file),
                            os.path.join(result_folder, file))




    def clean_working_files(self):
        """
        Delete the files which where created from pylot and profast.
        The files to be deleted are:
        - Input file for preprocess:
            - proffast/prf/preprocess/preprocess4.inp
        - Input file for pxcs10 and inver10:
            - proffast/prf/inp_fast/invers10_date.inp
            - proffast/prf/inp_fast/pcxs10_date.inp
        - abscos-bin files:
            - proffast/prf/wrk_fast/SiteDate-abscos.bin
        """
        pass

    def collate_results(self):
        pass
