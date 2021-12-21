import os
import sys
import datetime as dt


class InputfileGenerator():
    """Generation of input files.

    functions:
        generate_sod_example: create an input file for the provided
            example data of Sodankyla.
        interactive_inputfile_generation: fill in the required information
            in a command line dialogue.
    """
    def __init__(self):
        """Create an input file for the provided example data of Sodankyla.
        """

        self.scriptpath = os.path.abspath(os.path.dirname(__file__))
        self.inptfl_template = os.path.join(self.scriptpath, "templates",
                                            "template_input.yml")
        # a dict where the config is safed:
        self.input_data = {}

    def generate_sod_example(self):
        """
        This methods contains the hardcoded path to the example files
        """
        # the path where the final inputfile is writte to
        self.inptfl_path = os.path.join(self.scriptpath, "..", "example")
        self.inptfl = os.path.join(
                                self.inptfl_path,
                                "input_sodankyla_example.yml")
        # the data which is used to fill the template
        self.input_data["instrument_number"] = "SN039"
        self.input_data["site_name"] = "Sodankyla"
        self.input_data["site_abbrev"] = "so"
        self.input_data["lat"] = ""
        self.input_data["lon"] = ""
        self.input_data["alt"] = ""
        self.input_data["coord_file"] = ""
        self.input_data["utc_offset"] = ""
        self.input_data["start_date"] = ""
        self.input_data["end_date"] = ""
        self.input_data["note"] = ""
        inputpath = os.path.join(
            self.scriptpath, "..", "example",
            "input_data")
        igram_path = os.path.join(inputpath, "inteferograms_sodankyla",
                                  "SN039")
        self.input_data["interferogram_path"] = os.path.normpath(igram_path)
        map_path = os.path.join(inputpath, "map_sodankyla")
        self.input_data["map_path"] = os.path.normpath(map_path)

        pressure_path = os.path.join(inputpath, "pressure_sodankyla")
        self.input_data["pressure_path"] = os.path.normpath(pressure_path)        
        
        # TODO: Check if this changes in a later version
        result_path = os.path.join(self.scriptpath, "..", "example", "result")
        self.input_data["result_path"] = os.path.normpath(result_path)
        
        # TODO: Check if this folder changes in case of an example
        analysis_path = os.path.join(self.scriptpath, "..", "prf", "analysis")
        self.input_data["analysis_path"] = os.path.normpath(analysis_path)

        # TODO: Check if prf_path changed in case of the example.
        prf_path = os.path.join(self.scriptpath, "..", "prf")
        self.input_data["proffast_path"] = prf_path

        self._generate_inputfile()

    def interactive_inputfile_generation(self):
        """
        Generate the input file interactivly with a command line dialogue.
        """
        hashtg = "####################"
        spaces = "                    "
        print(
            f"#{hashtg}######################################{hashtg}#\n"
            f"#{spaces}  Welcome to the inputfile generator. {spaces}#\n"
            f"#{spaces}  This tool is part of the prfPylot.  {spaces}#\n"
            f"#{hashtg}######################################{hashtg}#\n"
        )

        temp = input("To start the configuration press enter")
        print("############ Data paths ############\n")
        temp = input("Please give the path of the PROFFAST executable:\n")
        self.input_data["proffast_path"] = temp

        temp = input("\nPlease give the path of the interferograms.\n"
                     "The data has to be stored there in subfolder with "
                     "the convention 'YYMMDD/YYMMDDSN.XXX':\n")
        self.input_data["interferogram_path"] = temp

        temp = input("\nPlease give the path of the map files:\n")
        self.input_data["map_path"] = temp

        temp = input("\nPlease give the path of the pressure files:\n")
        self.input_data["pressure_path"] = temp

        temp = input("\nPlease give the path of the analysis folder.\n"
                     "In a standard installation it located in the same folder"
                     " as the PROFFAST executables:\n")
        self.input_data["analysis_path"] = temp

        temp = input(
            "\nPlease give the path where the results are going to be "
            "stored:\n")
        self.input_data["result_path"] = temp

        print("\n\n############ Site Specific Information ############\n")
        temp = input("Please give the name of your site (e.g. Sodankyla):\n")
        self.input_data["site_name"] = str(temp)

        temp = input("\nPlease give the instrument number (e.g. SN039):\n")
        self.input_data["instrument_number"] = str(temp)

        temp = input("\nPlease give the site abbeviation as given in the map"
                     "-files:\n")
        self.input_data["site_abbrev"] = temp

        temp = input("\nCoordinates:\n"
                     "Do you want to specify coordinates or do you want to"
                     " use the coordinates given in the coordinate file?\n"
                     "Please write either 'custom' or 'file':\n")
        while True:
            if temp == "custom" or temp == "file":
                break
            else:
                temp = input("Could not read input!\n"
                             "Please give either 'file'"
                             " for taking the coordinate from the file or "
                             "'custom' if you want to specify them in the"
                             " following:\n")
        if temp == "file":
            self.input_data["lat"] = ""
            self.input_data["lon"] = ""
            self.input_data["alt"] = ""
            temp = input("\nPlease give the path to the coord-file. "
                         "If nothing is entered the default path"
                         "(rootpath/TODO!!!!) is used:\n")
            self.input_data["coord_file"] = temp
        elif temp == "custom":
            self.input_data["coord_file"] = ""
            print("NOTE: Please give the coordinates with an accuracy of"
                  " 5 digits!")
            abbrv = ["lat", "lon"]
            coord_text = ["latitude", "longitude"]
            for i, coord in enumerate(coord_text):
                temp = input(f"Please give the {coord}:\n")
                while True:
                    try:
                        temp = float(temp)
                        break
                    except ValueError:
                        temp = input("Could not read input. Please give a "
                                     "Number with 5 digits and a dot as  "
                                     "decimal sign:\n")
                self.input_data[abbrv[i]] = "{:07.5f}".format(temp)
            temp = input("\nPlease give the altitude in meter:\n")
            while True:
                try:
                    temp = float(temp)
                    break
                except ValueError:
                    temp = input("Could not parse input. Please give a "
                                 "Number:\n")
            self.input_data["alt"] = temp
            
        # TODO: Find out in which format the UTC-offset is needed.
        temp = input(
            "\nIf your igrams have a UTC-offset plase give it "
            "here: \n")
        self.input_data["utc_offset"] = temp

        print(
            "\nIf you do not want to process all interferograms of your site\n"
            "you can now specify a start and stop date.\n"
            "Leave it empty if you want to process all data:\n")
        strt_stp = ["start", "end"]
        for i, strtstp in enumerate(strt_stp):
            temp = input(f"Please give the {strtstp} date in YYYY-MM-DD:\n")
            if temp == "":
                self.input_data[f"{strtstp}_date"] = ""
            else:
                while True:
                    try:
                        temp = dt.date.fromisoformat(temp)
                        break
                    except ValueError:
                        temp = input(
                            "Could not parse input. Plase give as "
                            "YYYY-MM-DD:\n")
                self.input_data[f"{strtstp}_date"] = temp.isoformat()

        temp = input(
            "\nIf you want to add some notes to the spectra files please give"
            " it here. Limited to 80 characters:\n")
        while True:
            if len(temp) < 80:
                self.input_data["note"] = temp
                break
            else:
                temp = input("Note was to long. Give a shorter one:\n")

        print("\n############ Config file path ############\n")
        temp = input("Please give the path (not the name!) where the new "
                     "config-file is supposed to be stored:\n")
        self.inptfl_path = temp
        temp = input("\nPlease give the filename of the new config file. "
                     "If nothing is given the filename will be \n"
                     "'input_sitename_instrumentname.yml':\n")
        if temp == "":
            temp = f"{self.input_data['site_name']}_"\
                   + f"{self.input_data['instrument_number']}.yml"
            self.inptfl = os.path.join(self.inptfl_path, temp)
        elif temp[:-4] == ".yml":
            self.inptfl = os.path.join(self.inptfl_path, temp)
        elif temp[:-4] != ".yml":
            temp += ".yml"
            self.inptfl = os.path.join(self.inptfl_path, temp)
        # Finally we have all information we need. Create the file:
        self._generate_inputfile()

    def _generate_inputfile(self):
        """
        Generate the inpufile by replacing the %xxx% sections with the 
        corresponding value.
        """ 
        templ_stream = open(self.inptfl_template, 'r')
        config_stream = open(self.inptfl, 'w')
        for line in templ_stream:
            new_line = line
            for key, parameter in self.input_data.items():
                new_line = new_line.replace(
                    '%{}%'.format(key), str(parameter))
                new_line = self._replace_backslash(new_line)
            config_stream.write(new_line)
        templ_stream.close()
        config_stream.close()

    def _replace_backslash(self, line):
        """Replace backslash with slash if run on linux."""
        if sys.platform == "linux":
            return line.replace("\\", "/")
        return line


if __name__ == "__main__":
    import argparse

    MyGenerator = InputfileGenerator()
    parser = argparse.ArgumentParser()
    parser.add_argument("--example_mode",
                        help="Create the input file for the Sodankyla Example",
                        action="store_true")
    args = parser.parse_args()
    if args.example_mode:
        MyGenerator.generate_sod_example()
    else:
        MyGenerator.interactive_inputfile_generation()
