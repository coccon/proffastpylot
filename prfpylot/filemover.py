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

    def mv_spec_to_prf():
        """Move sectra to prf input folder?"""
        pass

    def move_bin_files():
        """Move binary files after running preprocessing"""
        pass

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
