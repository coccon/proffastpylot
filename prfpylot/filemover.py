from prfpylot.prepare import Preparation


class FileMover(Preparation):
    """Copy, Move and remove temporary profast Files."""
    def __init__(self, input_file):
        super(FileMover, self).__init__(input_file)
        self.input_file = input_file

    def mv_spec_to_prf():
        """Move sectra to prf input folder?"""
        pass

    def move_bin_files():
        """Move binary files after running preprocessing"""
        pass

    def remove_temporary_files_from_prf():
        """Remove all temporary files."""
        pass
