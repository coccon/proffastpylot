from prfpylot.filemover import FileMover
import pandas as pd
from subprocess import Popen, PIPE
import os
import time
import sys
from glob import glob
import multiprocessing
from timezonefinder import TimezoneFinder
import pytz


class Pylot(FileMover):
    """Start all Profast processes."""

    def __init__(self, input_file):
        super(Pylot, self).__init__(input_file)
        self.logger.debug('Initialized the FileMover')

    def run(self, n_processes=1):
        """Execute all processes of profast.

        Run preporcessing, pcxs, invers.
        The generated data is moved and merged in a result folder.
        """
        self.run_preprocess(NumberOfProcesses=n_processes)
        self.run_pcxs(NumberOfProcesses=n_processes)
        self.run_inv(NumberOfProcesses=n_processes)
        self.combine_results()

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

    def run_pcxs(self, NumberOfProcesses=1):
        """
        Main method to run pxcs. If NumberOfProcesses > 1, run_pcxs_at is
        called directly. Otherwise it is called via run_parallel
        """
        self.logger.info(f"Running pcxs with {NumberOfProcesses} task(s) ...")
        output = []
        if NumberOfProcesses <= 1:
            for date in self.dates:
                tmp_out = self.run_pcxs_at(date)
                output.append(tmp_out)

        else:
            tmp_out = self._run_parallel(self.run_pcxs_at,
                                         NumberOfProcesses)
            output = tmp_out
        self._write_logfile("pcsx", output)

    def run_inv(self, NumberOfProcesses=1):
        """
        Main method to run inv. If NumberOfProcesses > 1, run_inv_at is
        called directly. Otherwise it is called via run_parallel
        """
        self.logger.info(f"Running inv with {NumberOfProcesses} task(s) ...")
        output = []
        if NumberOfProcesses <= 1:
            for date in self.dates:
                tmp_out = self.run_inv_at(date)
                output.append(tmp_out)
        else:
            tmp_out = self._run_parallel(self.run_inv_at,
                                         NumberOfProcesses)
            output = tmp_out
        self._write_logfile("inv", output)

    def run_pcxs_at(self, date):
        self.logger.info(f"Running pcxs at {date.strftime('%Y-%m-%d')} ...")
        prf_path = os.path.join(self.base_path, "prf")
        pcxs_executable = os.path.join(prf_path, "pcxs10.exe")
        # pcxs_executable = os.path.join(prf_path, "SimplePrinter.exe")
        if sys.platform == "linux":
            pcxs_executable = os.path.join(
                prf_path, "pcxs10")
        self.generate_prf_input("pcxs", date)
        prf_input_path = os.path.basename(
            self.get_prf_input_path("pcxs", date))
        out, err = self._call_external_program(
            [pcxs_executable, prf_input_path], **{'cwd': prf_path})
        if err == "":
            err = "No Error occured."
        outlist = out, err, " ".join([pcxs_executable, prf_input_path])
        return outlist

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
        out, err = self._call_external_program(
                    [inv_executable, prf_input_path], **{'cwd': prf_path})
        outlist = out, err, " ".join([inv_executable, prf_input_path])
        return outlist

    def move_results(self):
        """
        Move the results to the data folder.
        If the datafolder does exists, the existing folder is renamed adding
        backupX where X increases if an other backup does already exists.
        After renaming, a new folder is created.
        """

        # check if result folder exist already, if not create
        if os.path.exists(self.result_path):
            # check if already other backuped folder exist as well:
            backuped_results = glob(self.result_path + "_backup*")
            # rename existing folder by adding _backupN where N is the N-th
            # backup
            result_folder_backup = self.result_path\
                + f"_backup{len(backuped_results)}"
            self.logger.warning(f"Result directory {self.result_path} exists!" +
                                "Renamed existing one to "
                                f"{result_folder_backup} and create a new one")
            # rename and create new, empty folder
            os.rename(self.result_path, result_folder_backup)
            os.makedirs(self.result_path)
        else:
            os.makedirs(self.result_path)
        # move result files to directory
        # files can be devided in suffix and preafix, where the suffix is
        # constant allt the time:
        suffix_list = [
            # "colsens.dat", 
            "invparms.dat", 
            "job01.spc",
            "job02.spc",
            "job03.spc",
            "job04.spc",
            "job05.spc"
        ]
        source_folder = os.path.join(self.base_path, "prf", "out_fast")
        for date in self.dates:
            datestr = date.strftime("%y%m%d")
            praefix = self.site_name + datestr + "-"
            for suffix in suffix_list:
                file = praefix + suffix
                shutil.move(os.path.join(source_folder, file),
                            os.path.join(self.result_path, file))

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

    def combine_results(self):
        """Combine the generated result files and save as csv."""
        self.move_results()
        
        df = self._get_merged_df()
        df = self._add_timezones_to(df)
        df = self._select_rename_cols(df)
        
        combined_file = os.path.join(
            self.result_path, "combined_invparms.csv")
        df.to_csv(combined_file, index=False)
    
    def _call_external_program(self, commandList, **kwargs):
        """
        This method calls a extrenal program and returns the output and the
        error
        """
        p = Popen(commandList, stdout=PIPE, stderr=PIPE, **kwargs)
        out, err = p.communicate()
        p.wait()
        out = out.decode("utf-8")
        err = err.decode("utf-8")
        return(out, err)

    def _run_parallel(self, method, NumberOfProcesses):
        """
        Run pcxs in parallel using python multiprocessing
        """
        pool = multiprocessing.Pool(processes=NumberOfProcesses)
        output = pool.map(method, self.dates)
        return output

    def _write_logfile(self, program, content):
        """
        This method writes the output of pcxs and inv to a logfile.
        """
        self.logger.info(f"Write Log-files of {program}")
        start_str = self.dates[0].strftime("%y%m%d")
        stop_str = self.dates[-1].strftime("%y%m%d")
        if not os.path.exists(self.logfile_path):
            self.logger.debug(
                f"Logfile path did not exist, create {self.logfile_path}")
            os.makedirs(self.logfile_path)
        self.logger.debug(f"Logfile_path: {self.logfile_path}")
        # TODO: Add PID or something similar to logfile?
        file = os.path.join(self.logfile_path,
                            f"LogFile_{program}_{start_str}_{stop_str}.txt")
        logfile = open(file, "w")
        for entry in content:
            out, err, call_strg = entry
            logfile.write("=============================================\n")
            logfile.write(call_strg)
            logfile.write("\nOutput:\n")
            logfile.write(out)
            logfile.write("\n\nErrors:\n")
            logfile.write(err)
            logfile.write("\n============================================\n\n")
        logfile.close()

    def _get_merged_df(self):
        """Read all invparm.dat files as Dataframe and combine them."""
        search_str = os.path.join(
            self.result_path, "*-invparms.dat")
        invparms_filelist = glob(search_str)

        df_list = [
            pd.read_csv(file, delim_whitespace=True)
            for file in invparms_filelist]
        df = pd.concat(df_list)

        return df

    def _add_timezones_to(self, df):
        """Add UTC and local timezone at measurement location."""
        df["JulianDate"] = df["JulianDate"]
        df["UTC"] = pd.to_datetime(
            df["JulianDate"].values, origin="julian", unit="D", utc=True)
        
        tf = TimezoneFinder()
        local_tz_name = tf.timezone_at(
            lat=self.coords["lat"],
            lng=self.coords["lon"])
        
        local_tz = pytz.timezone(local_tz_name)
        df["LocalTime"] = df["UTC"].dt.tz_convert(local_tz)
        return df

    def _select_rename_cols(self, df):
        """Return df with selected and renamed columns."""
        rename = {
            'job01_gas01': 'H2O',
            'job02_gas07': 'O2',
            'job03_gas03': 'CO2',
            'job04_gas04': 'CH4',
            'job05_gas06': 'CO',
            'job05_gas04': 'CH4_S5P'
        }
        df = df.rename(columns=rename)
        
        sel_cols = [
            "UTC", "LocalTime",
            "JulianDate", "HHMMSS_ID",
            "gndP", "gndT",
            "latdeg", "londeg",
            "appSZA", "azimuth",
            "XH2O", "XAIR",
            "XCO2", "XCH4",
            "XCO", "XCH4_S5P",
            "H2O", "O2",
            "CO2", "CH4",
            "CO", "CH4_S5P"
        ]
        df = df[[*sel_cols]]
        return df
