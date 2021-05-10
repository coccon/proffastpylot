import os
import yaml


class PRFpylot():
    """PROFAST wrapper."""

    def __init__(self, input_path="input.yml"):
        # read input file
        with open(input_path, "r") as f:
            args = yaml.load(f, Loader=yaml.FullLoader)

        # set parameters from input file
        self.coordinates = args["coordinates"]

        self.root_path = args["root_path"]
        if self.root_path == "default":
            cwd = os.getcwd()
            cwd = os.path.split(cwd)
            self.root_path = os.path.join(*cwd[:-1])

        self.map_path = args["map_path"]
        if self.map_path == "default":
            self.map_path = os.path.join(cwd, 'data',
                                         args['instrument_number'], 'map-Files'
                                         )
        self.pt_path = args["pt_path"]
        if self.pt_path == "default":
            # todo: decide if folder is 'log-Files', or 'met-Files'
            self.pt_path = os.path.join(cwd, 'data',
                                        args['instrument_number'], 'log-Files'
                                        )

        # set general parameters
        self.tempfiles = {
            "prep": None,
            "pt": None,
            "inv": None,
            "pcxs": None
        }

    def generate_template_file():
        pass
