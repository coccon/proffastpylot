import os
from glob import glob
import shutil
import pathlib

from prfpylot.prepare import Preparation


class FileMover(Preparation):
    """Copy, Move and remove temporary profast Files."""

    def __init__(self, input_file):
        super(FileMover, self).__init__(input_file)
        self.input_file = input_file

    def mv_spec_to_prf():
        """Move sectra to prf input folder?"""
        pass

    def move_bin_files(self, deleteExistingFolders=True):
        """Move binary files after running preprocessing"""
        # loop over all days which where processed:
        print("INFO: Start Moving files")
        for date in self.dates:
            # the *.BIN files are currently in the self.igram_path/YYMMDD/cal
            # folder. search for them:
            date_str = date.strftime("%y%m%d")
            bin_files = glob(os.path.join(self.igram_path, date_str,
                             "cal", "*.BIN"))
            # they should be in self.spectra_path/YYMMDD/cal/*.bin:
            target_folder = os.path.join(self.spectra_path, date_str, "cal")
            if os.path.exists(target_folder) and deleteExistingFolders:
                # delete the folder and make it new
                shutil.rmtree(target_folder)
                os.mkdir(target_folder)
                os.makedirs(target_folder, exist_ok=True)
            else:
                os.makedirs(target_folder, exist_ok=True)
            print(f"INFO: Move files of date {date_str}")
            for bin_file in bin_files:
                file_name = os.path.basename(bin_file)
                print(f"DEBUG:\n{bin_file}\n{file_name}")
                shutil.move(bin_file, os.path.join(target_folder, file_name))

    def remove_temporary_files_from_prf():
        """Remove all temporary files."""
        pass

    def get_map_file(self, date):
        """Return path to mapfile of given date.

        params:
            date: datetime object
        """
        search_string = os.path.join(
            self.map_path,
            "*{date}.map".format(date=date.strftime("%y%m%d")))
        map_file = glob(search_string)

        assert len(map_file) == 1
        map_file = map_file[0]

        return map_file
