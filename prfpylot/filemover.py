import os
from glob import glob
import shutil
from prfpylot.prepare import Preparation


class FileMover(Preparation):
    """Copy, Move and remove temporary profast Files."""

    def __init__(self, input_file, logginglevel="info"):
        super(FileMover, self).__init__(input_file, logginglevel=logginglevel)
        # create all folders
        self.init_folders()

    def init_folders(self):
        """Create all relevant folders on startup if nonexistant.

        Check if relevant profast folders are existant.
        Folders to be created:
        - pT, cal directories
        - result folder (backup of previous results)
        - logfiles
        """
        self._check_proffast_folders()
        for date in self.dates:
            self._create_pT_dir(date)
            self._create_cal_dir(date)
        self._create_result_dir()
        self._create_logfile_dir()
        self._create_spectra_outputfolder()

    def _create_spectra_outputfolder(self):
        """This method creates a folder for each day of the input igrams in
        the spectra output folder. 
        """
        for date in self.dates:
            datestring = date.strftime("%y%m%d")
            outfolder = os.path.join(self.spectra_path, datestring, "cal")
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)
            else:
                self.logger.warning(f"Spectra folder for date {datestring}"
                                    " exists already."
                                    " Content may be overwritten.")

    def _check_proffast_folders(self):
        """Check if relevant Profast folders are in place."""
        pass

    def _create_pT_dir(self, date):
        """Create pt directory."""
        pt_path = os.path.join(
            # TODO: Check if this is correct
            # self.data_path,
            self.spectra_path,
            date.strftime("%y%m%d"),
            "pT")
        if not os.path.exists(pt_path):
            os.makedirs(pt_path)

    def _create_cal_dir(self, date):
        """Create the cal dir in the interferogram folder, overwrite if exists.
        """
        date_str = date.strftime("%y%m%d")
        igram_folder = os.path.join(self.igram_path, date_str)
        cal_path = os.path.join(igram_folder, 'cal')
        if os.path.exists(cal_path):
            shutil.rmtree(cal_path)
        os.mkdir(cal_path)

    def _create_result_dir(self):
        """Create a result dir and a backup if previous results exist.

        If the datafolder does exists, the existing folder is renamed adding
        backupX where X increases if an other backup does already exists.
        After renaming, a new folder is created.
        """
        # The result_foldername and result dir are already specified in
        # the init of prepare

        if os.path.exists(self.result_folder):
            # check if already other backuped folder exist as well:

            backuped_results = glob(self.result_folder + "_backup*")
            # rename existing folder by adding _backupN where N is the N-th
            # backup
            result_folder_backup = self.result_folder\
                + f"_backup{len(backuped_results)}"
            self.logger.warning(
                f"Result directory {self.result_folder} exists! "
                "Renamed existing one to "
                f"{result_folder_backup} and created a new one.")
            # rename and create new, empty folder
            os.rename(self.result_folder, result_folder_backup)
            os.makedirs(self.result_folder)
        else:
            os.makedirs(self.result_folder)

    def move_results(self):
        """Move the results to the data folder.
        """
        suffix_list = [
            "colsens.dat",
            "invparms.dat",
            "job01.spc",
            "job02.spc",
            "job03.spc",
            "job04.spc",
            "job05.spc"
        ]
        source_folder = os.path.join(self.proffast_path, "out_fast")
        for date in self.dates:
            datestr = date.strftime("%y%m%d")
            prefix = self.site_name + datestr + "-"
            for suffix in suffix_list:
                file = prefix + suffix
                source = os.path.join(source_folder, file)
                target = os.path.join(self.result_folder, file)
                try:
                    shutil.move(source, target)
                except FileNotFoundError:
                    self.logger.error(f"File {source} was not found!")
                except PermissionError:
                    self.logger.error(f"Could not write {target} due to "
                                      "permission issues.")
                except OSError as e:
                    self.logger.error("Unknown error while movig file "
                                      f"{source}. Errormessage: {e}")

    def delete_abscos_files(self):
        """Delete the abscos.bin files."""
        wrk_fast_folder = os.path.join(self.proffast_path, "wrk_fast")
        for date in self.dates:
            filename = f"{self.site_name}{date.strftime('%y%m%d')}-abscos.bin"
            try:
                os.remove(os.path.join(wrk_fast_folder, filename))
            except FileNotFoundError:
                self.logger.warning("File not Found: "
                                    f"Could not move {source}")

    def move_abscos_files(self):
        """Move abscos.bin files to result folder"""
        wrk_fast_folder = os.path.join(self.proffast_path, "wrk_fast")
        # the target folder doesnot exists, since this is an optional method
        abscosbin_folder = os.path.join(self.result_folder, "abscos-bin")
        if not os.path.exists(abscosbin_folder):
            os.mkdir(abscosbin_folder)
        for date in self.dates:
            filename = f"{self.site_name}{date.strftime('%y%m%d')}-abscos.bin"
            try:
                source = os.path.join(wrk_fast_folder, filename)
                target = os.path.join(abscosbin_folder, filename)
                shutil.move(source, target)
            except FileNotFoundError:
                self.logger.warning("File not Found: "
                                    f"Could not move {source}")

    def delete_input_files(self):
        """Delete the input files for preprocess, pcxs and inv"""
        for i, date in enumerate(self.dates):
            for type in ["prep", "pcxs", "inv"]:
                inp_file = self.get_prf_input_path(type, date)
                try:
                    os.remove(inp_file)
                except FileNotFoundError:
                    self.logger.warning("File not Found: "
                                        f"Could not remove {type} input file"
                                        f" {inp_file}")

    def move_input_files(self):
        """Move the input files for prep., pcxs and inv to result folder"""
        # crate a folder in result dir for input files:
        inp_folder = os.path.join(self.result_folder, "input_files")
        if not os.path.exists(inp_folder):
            os.mkdir(inp_folder)

        for type in ["prep", "pcxs", "inv"]:
            for i, date in enumerate(self.dates):
                inp_file = self.get_prf_input_path(type, date)
                try:
                    shutil.move(
                        inp_file,
                        os.path.join(inp_folder, os.path.basename(inp_file)))
                except FileNotFoundError:
                    self.logger.warning("File not found: "
                                        f"Could not move {type} input file"
                                        f" {inp_file}")

    def _create_logfile_dir(self):
        """Create logfile dir if is does not exist."""
        if not os.path.exists(self.logfile_path):
            self.logger.debug(
                f"Logfile path did not exist, create {self.logfile_path}")
            os.makedirs(self.logfile_path)
        self.logger.debug(f"Logfile_path: {self.logfile_path}")

    def _move_generallogfile_to_logdir(self):
        """Move the general logfile to the logdir"""
        # This have to be done at the end, since the folder is createt by the
        # program itself.
        for i, handler in enumerate(self.logger.handlers[:]):
            if i == 1:
                # TODO: BUGFIX!! Here happens some kind of black-python-magic
                #       As soon as the below statement is printed an error
                #       occurs at a place where I do not expect it..?
                # print(isinstance(logger, logging.FileHandler))
                #print(handler)
                handler.close()
                self.logger.removeHandler(handler)
                del handler
            # self.logger.handlers[:][1].close()
        target = os.path.join(self.logfile_path,
                              os.path.basename(self.generalLogfile))
        try:
            shutil.move(self.generalLogfile, target)
            self.logger.info("Moved the general logfile to the"
                             " result/logfiles folder")
        except (FileNotFoundError) as e:
            self.logger.debug(f"\nsource: {self.generalLogfile} "
                              f"\ntarget: {target}")
            self.logger.debug(e)
            self.logger.error("Could not move logfile to new logfile dir! "
                              f"File is located in: {self.generalLogfile}")        
