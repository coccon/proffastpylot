import os
from glob import glob
import datetime as dt
import shutil
from prfpylot.prepare import Preparation


class FileMover(Preparation):
    """Copy, Move and remove temporary profast Files."""

    def __init__(self, input_file):
        super(FileMover, self).__init__(input_file)
        self.input_file = input_file

    def create_work_dirs():
        """Create profast work directories, if non-existant."""
        dirs = ["inp_fwd", "out_fast"]
        for d in dirs:
            if not os.path.exists(d):
                shutil.makedir(d)

    def create_temporary_pT_dir(self, date):
        """Create empty directory."""
        pt_path = os.path.join(
            self.data_path,
            dt.strftime(date, "%y%m%d"),
            "pT")
        if not os.path.exists(pt_path):
            shutil.makedir(pt_path)

    def create_cal_dirs(self):
        for date in self.dates:
            date_str = date.strftime("%y%m%d")
            igram_folder = os.path.join(self.data_path, date_str)
            cal_path = os.path.join(igram_folder, 'cal')
            if os.path.exists(cal_path):
                shutil.rmtree(cal_path)
            os.mkdir(cal_path)

    def mv_spec_to_prf():
        """Move sectra to prf input folder?"""
        pass

    def move_bin_files(self, overwrite=True):
        """Move binary files after running preprocessing"""
        # loop over all days which where processed:
        self.logger.info("Start Moving files")
        for date in self.dates:
            # the *.BIN files are currently in the self.data_path/YYMMDD/cal
            # folder. search for them:
            date_str = date.strftime("%y%m%d")
            bin_files = glob(os.path.join(self.data_path, date_str,
                             "cal", "*.BIN"))
            # they should be in self.spectra_path/YYMMDD/cal/*.bin:
            target_folder = os.path.join(self.spectra_path, date_str, "cal")
            if os.path.exists(target_folder) and overwrite:
                # delete the folder and make it new
                shutil.rmtree(target_folder)
                os.makedirs(target_folder, exist_ok=False)
            else:
                os.makedirs(target_folder, exist_ok=True)
            self.logger.info(f"Move files of date {date_str}")
            for bin_file in bin_files:
                file_name = os.path.basename(bin_file)
                target = os.path.join(target_folder, file_name)
                shutil.move(bin_file, target)
                self.logger.debug(f"Moved {bin_file}->{target}")

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

    def delete_abscos_files(self):
        """Delete the abscos.bin files."""
        wrk_fast_folder = os.path.join(
            self.base_path, "wrk_fast")
        # TODO: Implement deletion
        pass
        
    def remove_temporary_files_from_prf():
        """Remove all temporary files."""
        pass

    def create_logfile_dir(self):
        if not os.path.exists(self.logfile_path):
            self.logger.debug(
                f"Logfile path did not exist, create {self.logfile_path}")
            os.makedirs(self.logfile_path)
        self.logger.debug(f"Logfile_path: {self.logfile_path}")
