"""Pylot is a module of PROFFASTpylot.

Steer all parts of PROFFASTpylot by initialising an instance of the
Pylot class and executing the different run methods.
See also in proffastpylot/doc for more inforamation about the usage.

License information:
PROFFASTpylot - Running PROFFAST with Python
Copyright (C)   2022    Lena Feld, Benedikt Herkommer,
                        Karlsruhe Institut of Technology (KIT)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from prfpylot.filemover import FileMover
from prfpylot.pressure import \
    generate_pt_intraday, prepare_pressure_df
import pandas as pd
from subprocess import Popen, PIPE
import os
import sys
from glob import glob
import multiprocessing
from timezonefinder import TimezoneFinder
import pytz
import shutil
import numpy as np
import logging
from logging.handlers import QueueHandler
from functools import partial
import yaml


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
            f"Running preprocess with {n_processes} task(s) ...")
        # check if TCCON Mode is activated. If yes create the tccon input file
        if self.tccon_mode:
            self.logger.debug("...create tccon file...")
            self.generate_prf_input("tccon")
        else:
            # check if TCCON file is present by accident. If yes delete it
            tccon_file = self.get_prf_input_path("tccon")
            if os.path.exists(tccon_file):
                os.remove(tccon_file)
                self.logger.warning(
                    "Found TCCON file, which was not expected."
                    "Delete it for normal processing.")

        # a Queue to save all days where all interferograms are bad
        m = multiprocessing.Manager()
        self.badDayQ = m.Queue()

        output = []
        if n_processes <= 1:
            for date in self.dates:
                tmp_out = self.run_preprocess_at(date, self.badDayQ)
                output.append(tmp_out)
        else:
            self.logger.debug("...start parallel processing...")
            tmp_out = self._run_parallel(self.run_preprocess_at, n_processes)
            output = tmp_out
        self._write_logfile("preprocess", output)

        self._check_for_bad_days()

        if self.tccon_mode:
            # delete tccon input file:
            os.remove(self.tccon_file)
            self.logger.debug("... delete TCCON file")
        self.logger.info("Finished preprocessing.\n")

    def run_pcxs(self, n_processes=1):
        """
        Main method to run pxcs. If n_processes > 1, run_pcxs_at is
        called directly. Otherwise it is called via run_parallel
        """
        self.logger.info(f"Running pcxs with {n_processes} task(s) ...")
        # ensure that the badDayQ is empty:
        if self.start_with_spectra:
            # The Queue to save all days where all interferograms are bad
            # must be created here, if not available by run_preprocess
            m = multiprocessing.Manager()
            self.badDayQ = m.Queue()

        while not self.badDayQ.empty():
            self.badDayQ.get()

        output = []
        if n_processes <= 1:
            for date in self.dates:
                tmp_out = self.run_pcxs_at(date, badDayQ=self.badDayQ)
                output.append(tmp_out)

        else:
            tmp_out = self._run_parallel(self.run_pcxs_at,
                                         n_processes)
            output = tmp_out
        self._write_logfile("pcsx", output)
        self._check_for_bad_days()
        self.logger.info("Finished pcxs.\n")

    def run_inv(self, n_processes=1):
        """Run inverse.
        If n_processes > 1, run_inv_at() is called directly.
        Otherwise it is called via run_parallel.
        """
        self.logger.info(f"Running invers with {n_processes} task(s) ...")
        output = []

        # read in the pressure for all days in self.dates.
        # returns the dataframe containing the ready to use data for proffast
        pressure_DataFrame = prepare_pressure_df(
            self.pressure_path, self.pressure_args, self.dates)

        if n_processes <= 1:
            for date in self.dates:
                tmp_out = self.run_inv_at(
                    date, pressure_df=pressure_DataFrame)
                output.append(tmp_out)
        else:
            kwargs = {"pressure_df": pressure_DataFrame}
            tmp_out = self._run_parallel(self.run_inv_at,
                                         n_processes,
                                         kwargs=kwargs)
            output = tmp_out
        self._check_for_bad_days()
        self._write_logfile("inv", output)
        self.logger.info("Finished invers.\n")

    def run_preprocess_at(self, date, badDayQ, loggingq=None):
        """Run preprocess at date."""
        # for multiprocessing create a new logger:
        if loggingq is not None:
            mlogger = logging.getLogger("mLogger")
            mlogger.setLevel(logging.DEBUG)
            q_handler = QueueHandler(loggingq)
            q_handler.setLevel(level=logging.DEBUG)
            mlogger.addHandler(q_handler)
        else:
            mlogger = self.logger

        mlogger.info("Running preprocess at "
                     f"{date.strftime('%Y-%m-%d')} ...")
        foundIgrams = self.generate_prf_input("prep", date, mlogger)
        if not foundIgrams:
            mlogger.warning(f"Do not execute preprocess at date {date} since"
                            " no suitable interferograms where found!")
            badDayQ.put(date)
            output = [f"Do not execute preprocess at date {date}.",
                      "No suitable iterferograms found",
                      f"No call string for date {date}.\n"]
            return output

        inputfile = os.path.basename(
            self.get_prf_input_path("prep", date))

        executable = self._get_executable("prep")
        exec_path = os.path.dirname(executable)

        outlist = ["only test mode here"]
        out, err = self._call_external_program(
            [executable, inputfile], mlogger, **{'cwd': exec_path})
        outlist = out, err, " ".join([executable, inputfile])
        return outlist

    def run_pcxs_at(self, date, loggingq=None, badDayQ=None):
        """ Run pcxs at date."""
        # for multiprocessing create a new logger:
        if loggingq is not None:
            mlogger = logging.getLogger("mLogger")
            mlogger.setLevel(logging.DEBUG)
            q_handler = QueueHandler(loggingq)
            q_handler.setLevel(level=logging.DEBUG)
            mlogger.addHandler(q_handler)
        else:
            mlogger = self.logger
        mlogger.info(f"Running pcxs at {date.strftime('%Y-%m-%d')} ...")

        # Check if the abscos.bin files are already available, if yes skip the
        # day
        wrk_fast_path = os.path.join(self.proffast_path, "wrk_fast")
        srchstrg = f"{self.site_name}{date.strftime('%y%m%d')}-abscos.bin"
        if os.path.exists(os.path.join(wrk_fast_path, srchstrg)):
            message = (
                f"*.abscos.bin file for day {date} exists already."
                " Skip calculation..")
            mlogger.info(message)
            return [message, "No Error", "No call String"]

        foundSpectra = self.generate_prf_input(
            "pcxs", date, mlogger=mlogger)
        if not foundSpectra:
            mlogger.warning(f"Do not execute pcxs at date {date} since"
                            " no suitable spectra where found!")
            badDayQ.put(date)
            output = [f"Do not execute pcxs at date {date}.",
                      "No suitable spectra found",
                      f"No call string for date {date}.\n"]
            return output

        # search for GGG2020 map files:
        srchstrg = f"{self.site_abbrev}_*_*Z.map"
        mapfiles = glob(os.path.join(self.map_path, srchstrg))
        if len(mapfiles) != 0:
            self.logger.debug("Detected GGG2020 map files!")
            # GGG2020map files found!
            self.ggg2020mapfiles = True
            self._interpolate_map_files(date)
        else:
            srchstrg = f"{self.site_abbrev}{date.strftime('%Y%m%d')}.map"
            mapfiles = glob(os.path.join(self.map_path, srchstrg))
            if len(mapfiles) == 1:
                self.logger.debug("Detected GGG2014 map file!")
                self.ggg2020mapfiles = False
            else:
                self.logger.critical(
                    "No suitable map file found at "
                    f"{self.map_path} for {date.strftime('%Y-%m-%d')}.")
                sys.exit()

        prf_input_path = os.path.basename(
            self.get_prf_input_path("pcxs", date))

        executable = self._get_executable("pcxs")
        out, err = self._call_external_program(
            [executable, prf_input_path], **{'cwd': self.proffast_path})

        outlist = out, err, " ".join([executable, prf_input_path])
        return outlist

    def run_inv_at(self, date, loggingq=None, badDayQ=None, pressure_df=None):
        # for multiprocessing create a new logger:
        if loggingq is not None:
            mlogger = logging.getLogger("mLogger")
            mlogger.setLevel(logging.DEBUG)
            q_handler = QueueHandler(loggingq)
            q_handler.setLevel(level=logging.DEBUG)
            mlogger.addHandler(q_handler)
        else:
            mlogger = self.logger
        self.logger.debug(f"Run inv at date {date.isoformat()}")

        foundSpectra = self.generate_prf_input(
            "inv", date, mlogger=mlogger)
        if not foundSpectra:
            mlogger.warning(f"Do not execute inv at date {date} since"
                            " no spectra where found!")
            badDayQ.put(date)
            output = [f"Do not execute inv at date {date}.",
                      "No suitable spectra found",
                      f"No call string for date {date}.\n"]
            return output

        self.prepare_pressure_at(date, mlogger, pressure_df)
        prf_input_path = os.path.basename(
            self.get_prf_input_path("inv", date))
        executable = self._get_executable("inv")
        out, err = self._call_external_program(
                    [executable, prf_input_path],
                    **{'cwd': self.proffast_path})
        outlist = out, err, " ".join([executable, prf_input_path])
        return outlist

    def prepare_pressure_at(self, date, mlogger=None, pressure_df=None):
        """Perpare the pressure input data for a date.

        Depending on the options the pt_intraday file is either generated
        or copied to its destination for each day.
        """
        # extra logger for case of multiprocessing:
        if mlogger is None:
            mlogger = self.logger
        mlogger.debug("Call 'prepare_pressure_at'")
        date_str = date.strftime("%y%m%d")
        pt_folder = os.path.join(self.analysis_instrument_path, date_str, "pT")
        intraday_file = os.path.join(pt_folder, "pT_intraday.inp")

        if self.pressure_type == "original":
            filename = "{}_{}.inp".format(
                self.site_abbrev, date.strftime("%y-%m-%d"))
            src_intraday_file = os.path.join(
                self.intraday_path, filename)
            shutil.copy(src_intraday_file, intraday_file)
            return
        # =====================================================================
        # =====================================================================
        p_list = pressure_df[date]

        # =====================================================================
        # =====================================================================

        template_path = os.path.join(
            self.prfpylot_path, "templates", "template_pt_intraday.inp"
            )
        pt_intraday = generate_pt_intraday(p_list, template_path)

        with open(intraday_file, "w") as f:
            f.write(pt_intraday)

    def combine_results(self):
        """Combine the generated result files and save as csv."""
        self.logger.debug("Moving results to final output folder ...")
        self.move_results()

        df = self._get_merged_df()
        df = self._add_timezones_to(df)
        df = self._select_rename_cols(df)

        resultfile = "combined_invparms_{}_{}-{}.csv".format(
                            self.site_name,
                            self.dates[0].strftime("%Y%m%d"),
                            self.dates[-1].strftime("%Y%m%d")
                            )
        combined_file = os.path.join(
            self.result_folder, resultfile)
        df["UTC"] = df["UTC"].apply(lambda x: x.strftime("%Y-%m-%d %X"))
        df["LocalTime"] = df["LocalTime"].apply(
            lambda x: x.strftime("%Y-%m-%d %X"))

        format_list = [
            "%s", "%s", "%12.5f", "%6.1f", "%5.2f", "%5.2f", "%7.5f", "%7.5f",
            "%4.2f", "%5.2f", "%.5e", "%.5e", "%.5e", "%.5e", "%.5e", "%.5e",
            "%.5e", "%.5e", "%.5e", "%.5e", "%.5e", "%.5e"
                      ]
        np.savetxt(combined_file, df.values, fmt=format_list,
                   delimiter=', ', header=', '.join(df.columns), comments='')

        self.logger.info(
            "The combined results of PROFFAST were written "
            f"to {combined_file}.")

    def clean_files(self):
        """After execution clean up the files not needed anymore"""
        self.logger.info("Removing temporary files ...")

        # handling abscosbin
        if self.delete_abscosbin:
            self.logger.debug("Deleting abscos.bin files ...")
            self.delete_abscos_files()
        else:
            self.logger.info(
                "Keeping abscos.bin files ...\n"
                "They are located in "
                f"{os.path.join(self.proffast_path, 'wrk-fast')}.")
            self.check_abscosbin_summed_size()

        # handling input files
        if self.bool_delete_input_files:
            self.logger.debug("Deleting input files ...")
            self.delete_input_files()
        else:
            self.logger.debug("Moving input files ...")
            self.move_input_files()

        self._move_generallogfile_to_logdir()
        self._move_prf_config_file()
        self.logger.info("Done.")

    def _call_external_program(self, command_list, mlogger=None, **kwargs):
        """
        This method calls a external program and returns the output and the
        error
        """
        joined_commands = " ".join(command_list)
        if mlogger is None:
            mlogger = self.logger
        mlogger.debug("Command List: " + joined_commands)
        p = Popen(command_list, stdout=PIPE, stderr=PIPE, **kwargs)
        out, err = p.communicate()
        return_value = p.wait()
        out = out.decode("utf-8")
        err = err.decode("utf-8")

        if return_value != 0:
            mlogger.error(
                f"Error while processesing {joined_commands}!\n"
                f"PROFFAST error message: {err}")
        return (out, err)

    def _run_parallel(self, method, n_processes, kwargs={}):
        """Run method in parallel using python multiprocessing."""
        pool = multiprocessing.Pool(processes=n_processes)

        # create a queue for  multiprocessing logging:
        m = multiprocessing.Manager()
        logq = m.Queue(-1)
        subs_method = partial(
            method,
            badDayQ=self.badDayQ, loggingq=logq,
            **kwargs)
        output = pool.map(subs_method, self.dates)
        while not logq.empty():
            record = logq.get()
            self.logger.log(record.levelno, record.msg)

        return output

    def _write_logfile(self, program_name, output):
        """
        Write the output of preprocess, pcxs and inv to a logfile.
        """
        self.logger.debug(f"... Write logfile of {program_name} ...")

        file = os.path.join(self.logfile_path, f"{program_name}_output.log")

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
        file_params = self.pressure_args["filename_parameters"]
        filename = p_params.get_filename(file_params, date)
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

    def _check_for_bad_days(self):
        """If any badDays (i.e. no good igrams/spectra) occured delete the
        dates from the datelist
        """
        while not self.badDayQ.empty():
            badDay = self.badDayQ.get()
            self.dates.remove(badDay)
            self.logger.debug(f"Delete day {badDay.strftime('%Y-%m-%d')}"
                              " from processing list.")
