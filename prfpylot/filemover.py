import os
from glob import glob
import datetime as dt
import shutil
from prfpylot.prepare import Preparation


class FileMover(Preparation):
    """Copy, Move and remove temporary profast Files."""

    def __init__(self, input_file):
        super(FileMover, self).__init__(input_file)
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

    def _check_proffast_folders(self):
        """Check if relevant Profast folders are in place."""
        pass

    def _create_pT_dir(self, date):
        """Create pt directory."""
        pt_path = os.path.join(
            self.data_path,
            date.strftime("%y%m%d"),
            "pT")
        if not os.path.exists(pt_path):
            shutil.makedir(pt_path)

    def _create_cal_dir(self, date):
        """Create the cal dir in the interferogram folder, overwrite if exists.
        """
        date_str = date.strftime("%y%m%d")
        igram_folder = os.path.join(self.data_path, date_str)
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
        if os.path.exists(self.result_path):
            # check if already other backuped folder exist as well:
            backuped_results = glob(self.result_path + "_backup*")
            # rename existing folder by adding _backupN where N is the N-th
            # backup
            result_folder_backup = self.result_path\
                + f"_backup{len(backuped_results)}"
            self.logger.warning(f"Result directory {self.result_path} exists! "
                                "Renamed existing one to "
                                f"{result_folder_backup} and "
                                "created a new one.")
            # rename and create new, empty folder
            os.rename(self.result_path, result_folder_backup)
            os.makedirs(self.result_path)
        else:
            os.makedirs(self.result_path)

    def mv_spec_to_prf():
        """Move sectra to prf input folder?"""
        pass

    def move_bin_files(self, overwrite=True):
        """Move binary files after running preprocessing."""

        self.logger.debug("Start Moving files")
        for date in self.dates:
            date_str = date.strftime("%y%m%d")
            self.logger.info(f"Move files of date {date_str}")
            
            cal_folder = os.path.join(
                self.spectra_path, date_str, "cal")
            bin_files = glob(cal_folder, "*.BIN")            
            for bin_file in bin_files:
                file_name = os.path.basename(bin_file)
                target = os.path.join(cal_folder, file_name)
                shutil.move(bin_file, target)
                self.logger.debug(f"Moved {bin_file}->{target}")

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
        source_folder = os.path.join(self.base_path, "prf", "out_fast")
        for date in self.dates:
            datestr = date.strftime("%y%m%d")
            prefix = self.site_name + datestr + "-"
            for suffix in suffix_list:
                file = prefix + suffix
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

    def delete_abscos_files(self):
        """Delete the abscos.bin files."""
        wrk_fast_folder = os.path.join(
            self.base_path, "wrk_fast")
        # TODO: Implement deletion
        pass
        
    def remove_temporary_files_from_prf():
        """Remove all temporary files."""
        pass

    def _create_logfile_dir(self):
        """Create logfile dir if is does not exist."""
        if not os.path.exists(self.logfile_path):
            self.logger.debug(
                f"Logfile path did not exist, create {self.logfile_path}")
            os.makedirs(self.logfile_path)
        self.logger.debug(f"Logfile_path: {self.logfile_path}")
