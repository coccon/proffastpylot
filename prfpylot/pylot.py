from prfpylot.filemover import FileMover
from prfpylot.pressure import PressureParameters, \
    read_pressure_from_file, generate_pt_intraday
import pandas as pd
from subprocess import Popen, PIPE
import os
import sys
from glob import glob
import multiprocessing
from timezonefinder import TimezoneFinder
import pytz
import shutil


class Pylot(FileMover):
    """Start all Profast processes."""

    def __init__(self, input_file, logginglevel="info"):
        super(Pylot, self).__init__(input_file, logginglevel=logginglevel)
        
        self.logger.debug('Initialized the FileMover')

    def run(self, n_processes=1):
        """Execute all processes of profast.

        Run preporcessing, pcxs, invers.
        The generated data is moved and merged in a result folder.
        """
        try:
            self.run_preprocess(n_processes=n_processes)
            self.run_pcxs(n_processes=n_processes)
            self.run_inv(n_processes=n_processes)
            self.combine_results()
        finally:
            self.clean_files()

    def run_preprocess(self, n_processes=1):
        """Main method to run preprocess."""
        self.logger.info(
            f"Running preprocess4 with {n_processes} task(s) ...")
        output = []
        if n_processes <= 1:
            for date in self.dates:
                tmp_out = self.run_preprocess_at(date)
                output.append(tmp_out)
        else:
            self.logger.info("...start parallel processing...")
            tmp_out = self._run_parallel(self.run_preprocess_at, n_processes)
            output = tmp_out
        self._write_logfile("preprocess", output)        
        self.logger.info("... finished preprocessing.")

    def run_pcxs(self, n_processes=1):
        """
        Main method to run pxcs. If n_processes > 1, run_pcxs_at is
        called directly. Otherwise it is called via run_parallel
        """
        self.logger.info(f"Running pcxs with {n_processes} task(s) ...")
        output = []
        if n_processes <= 1:
            for date in self.dates:
                tmp_out = self.run_pcxs_at(date)
                output.append(tmp_out)

        else:
            tmp_out = self._run_parallel(self.run_pcxs_at,
                                         n_processes)
            output = tmp_out
        self._write_logfile("pcsx", output)

    def run_inv(self, n_processes=1):
        """
        Main method to run inv. If n_processes > 1, run_inv_at is
        called directly. Otherwise it is called via run_parallel
        """
        self.logger.info(f"Running inv with {n_processes} task(s) ...")
        output = []
        if n_processes <= 1:
            for date in self.dates:
                tmp_out = self.run_inv_at(date)
                output.append(tmp_out)
        else:
            tmp_out = self._run_parallel(self.run_inv_at,
                                         n_processes)
            output = tmp_out
        self._write_logfile("inv", output)

    def run_preprocess_at(self, date):
        """Run preprocess on a single day"""
        self.logger.info("Running preprocess at "
                         f"{date.strftime('%Y-%m-%d')} ...")
        self.generate_prf_input("prep", date)
        
        inputfile = os.path.basename(
            self.get_prf_input_path("prep", date))

        executable = self._get_executable("prep")
        exec_path = os.path.dirname(executable)
        
        outlist = ["only test mode here"]
        out, err = self._call_external_program(
            [executable, inputfile], **{'cwd': exec_path})
        outlist = out, err, " ".join([executable, inputfile])
        return outlist

    def run_pcxs_at(self, date):
        """ Run preprocess at a single day given as an argument """
        self.logger.info(f"Running pcxs at {date.strftime('%Y-%m-%d')} ...")
        # search for GGG2020 map files:
        srchstrg = f"{self.site_abbrev}_*_*Z.map"
        mapfiles = glob(os.path.join(self.map_path, srchstrg))
        if len(mapfiles) != 0:
            self.logger.info("Detected GGG2020 map files!")
            # GGG2020map files found!
            self.ggg2020mapfiles = True
            self._interpolate_map_files(date)
        else:
            srchstrg = f"{self.site_abbrev}{date.strftime('%Y%m%d')}.map"
            mapfiles = glob(os.path.join(self.map_path, srchstrg))
            if len(mapfiles) == 1:
                self.logger.info("Detected GGG2014 map file!")
                self.ggg2020mapfiles = False
            else:
                self.logger.critical("No suitable map file found. "
                                     f"Map-file path is: {self.map_path} "
                                     )
                raise(RuntimeError("No suitable map file found."))

        self.generate_prf_input("pcxs", date)
        prf_input_path = os.path.basename(
            self.get_prf_input_path("pcxs", date))

        executable = self._get_executable("pcxs")
        out, err = self._call_external_program(
            [executable, prf_input_path], **{'cwd': self.proffast_path})

        outlist = out, err, " ".join([executable, prf_input_path])
        return outlist

    def run_inv_at(self, date):
        self.logger.debug(f"Run inv at date {date.isoformat()}")
        self.prepare_pressure_at(date)
        
        self.generate_prf_input("inv", date)

        prf_input_path = os.path.basename(
            self.get_prf_input_path("inv", date))
        executable = self._get_executable("inv")
        out, err = self._call_external_program(
                    [executable, prf_input_path],
                    **{'cwd': self.proffast_path})
        outlist = out, err, " ".join([executable, prf_input_path])
        return outlist

    def prepare_pressure_at(self, date):
        """Perpare the pressure input data for a date.

        Depending on the options the pt_intraday file is either generated
        or copied to its destination for each day.
        """
        self.logger.debug("Call 'prepare_pressure_at'")
        date_str = date.strftime("%y%m%d")
        pt_folder = os.path.join(self.analysis_path, date_str, "pT")
        intraday_file = os.path.join(pt_folder, "pT_intraday.inp")

        if self.pressure_type == "original":
            filename = "{}_{}.inp".format(
                self.site_abbrev, date.strftime("%y-%m-%d"))
            src_intraday_file = os.path.join(
                self.intraday_path, filename)
            shutil.copy(src_intraday_file, intraday_file)
            return

        params = PressureParameters.dataframe_parameters[self.pressure_type]
        filename = self._get_pressure_file_at(date)
        pt_input_file = os.path.join(self.pressure_path, filename)
        p_list = read_pressure_from_file(
            file=pt_input_file,
            **params)

        template_path = os.path.join(
            self.prfpylot_path, "templates", "template_pt_intraday.inp"
            )
        pt_intraday = generate_pt_intraday(p_list, template_path)

        with open(intraday_file, "w") as f:
            f.write(pt_intraday)

    def combine_results(self):
        """Combine the generated result files and save as csv."""
        self.logger.info("Move results to final output folder")
        self.move_results()

        df = self._get_merged_df()
        df = self._add_timezones_to(df)
        df = self._select_rename_cols(df)
        # TODO: Create 
        resultfile = "combined_invparms_{}_StartStopDates{}_{}.csv".format(
                            self.site_name,
                            self.dates[0].strftime("%Y%m%d"),
                            self.dates[-1].strftime("%Y%m%d")
                            )
        combined_file = os.path.join(
            self.result_folder, resultfile)
        df.to_csv(combined_file, index=False, sep="\t",
                  float_format="%.5e")
        self.logger.info("Sucessfully wrote the combined invparams"
                         f" to {combined_file}")

    def clean_files(self):
        """After execution clean up the files not needed anymore"""
        if self.delete_abscosbin:
            self.logger.debug("Deleting abscos.bin files ...")
            self.delete_abscos_files()
        else:
            self.logger.info(
                "Keeping abscos.bin files ...\n"
                "They are located in "
                f"{os.path.join(self.proffast_path, 'wrk-fast')}.")
            self.check_abscosbin_summed_size()
        
        if self.bool_delete_input_files:
            self.logger.info("delete input files")
            self.delete_input_files()
        else:
            self.logger.info("Move input files")
            self.move_input_files()
        
        self._move_generallogfile_to_logdir()

    def _call_external_program(self, command_list, **kwargs):
        """
        This method calls a external program and returns the output and the
        error
        """
        joined_commands = " ".join(command_list)
        self.logger.debug("Command List: " + joined_commands)
        p = Popen(command_list, stdout=PIPE, stderr=PIPE, **kwargs)
        out, err = p.communicate()
        return_value = p.wait()
        out = out.decode("utf-8")
        err = err.decode("utf-8")

        if return_value != 0:
            self.logger.error(
                f"Error while processesing {joined_commands}!\n"
                f"PROFAST Error message: {err}")
        return (out, err)

    def _run_parallel(self, method, n_processes):
        """
        Run pcxs in parallel using python multiprocessing
        """
        pool = multiprocessing.Pool(processes=n_processes)
        output = pool.map(method, self.dates)
        return output

    def _write_preprocess_log(self, p_list):
        """Loop over list of processes and write output to logfile."""
        filename = "prfPylots_PreprocessLog_{}_{}.log".format(
                                    self.dates[0].strftime("%y%m%d"),
                                    self.dates[-1].strftime("%y%m%d"))
        logfile = os.path.join(self.logfile_path, filename)
        f = open((logfile), 'w')
        for c, p in enumerate(p_list):
            out, err = p.communicate()
            p.wait()
            out = out.decode('utf-8')
            err = err.decode('utf-8')
            if len(err) != 0:
                self.logger.error(
                    'Error while running preprocess\n' + err)
            f.write(
                f'\n===================== Task {c} =====================\n'
                f'Output of Preprocess Task {c}: \n {out}'
                f'Error of Preprocess: Task {c}\n {err}'
                '=====================================================\n'
            )
        f.close()
        self.logger.info(
            f"PROFFAST preprocess4 output was written to {logfile}")
        # TODO: Implement the following method in filemover!
        # self.rename_prep_internal_logfile(logfile)

    def _write_logfile(self, program_name, output):
        """
        Write the output of preprocess, pcxs and inv to a logfile.
        """
        self.logger.info(f"... Write logfile of {program_name} ...")

        # TODO: Add PID or something similar to logfile?
        file = os.path.join(self.logfile_path, f"Output_of_{program_name}.log")

        logfile = open(file, "w")
        for i, entry in enumerate(output):
            out, err, call_strg = entry
            logfile.write(f"\n================= Task {i} ================\n")
            logfile.write(call_strg)
            logfile.write("\nOutput:\n")
            logfile.write(out)
            logfile.write("\n\nErrors:\n")
            logfile.write(err)
            logfile.write("============================================\n")
            logfile.write("============================================\n\n\n")

        logfile.close()
        if err != "":
            self.logger.error(f"Error while running {program_name}:" + err)

    def _get_merged_df(self):
        """Read all invparm.dat files as Dataframe and combine them."""
        search_str = os.path.join(
            self.result_folder, "*-invparms.dat")
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
        # This needs to be executed, since the calls bevore took place in a
        # multiprocessing process, which is encapsulated and does not write to
        # the current instance of the class.
        if self.use_coordfile:
            self.get_coords_from_file(self.dates[0])
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

    def _get_executable(self, program):
        """Return PROFFAST executable of the given program part.

        Params:
            program (str): can be "prep", "pcxs" and "inv"

        Returns:
            executable (str): depending on the current operating system.
        """
        if program == "prep":
            executable = os.path.join(self.proffast_path, "preprocess",
                                      self.template_types[program])
        else:
            executable = os.path.join(self.proffast_path,
                                      self.template_types[program])

        if sys.platform == "win32":
            executable += ".exe"
        return executable

    def _get_pressure_file_at(self, date):
        """Return path to pressure file of given date."""
        p_params = PressureParameters()
        filename = p_params.get_filename(self.pressure_type, date)
        search_string = os.path.join(self.pressure_path, filename)
        
        pressure_file = glob(search_string)
        if len(pressure_file) == 0:
            self.logger.critical(
                f"Could not find pressure file {search_string}")
            raise RuntimeError("Could not find pressure file!")
        elif len(pressure_file) > 1:
            self.logger.critical(
                f"To many pressure files found matching {search_string}!")
            raise RuntimeError("Unambigous pressure files!")
        pressure_file = pressure_file[0]
        return pressure_file
