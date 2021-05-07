import yaml


class PRFpylot():
    """docstring for PRFpylot"""
    def __init__(self, input_path="input.yml"):
        # read input file
        with open(input_path, "r") as f:
            args = yaml.load(f)

        # set parameters from input file
        self.coordinates = args["coordinates"]

        self.map_path = args["map_path"]
        if self.map_path == "default":
            # Insert the default map path!
            pass
        self.pt_path = args["pt_path"]
        if self.pt_path == "default":
            # Insert the default pt path!
            pass

        # set general parameters
        self.tempfiles = {
            "prep": None,
            "pt": None,
            "inv": None,
            "pcxs": None
        }

    def generate_template_file():
        pass
