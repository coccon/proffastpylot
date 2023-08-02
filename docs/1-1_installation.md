# Installation

**For using PROFFASTpylot you need Python 3.7 or newer.**

## Content

1. Download the PROFFASTpylot repository
2. Get PROFFAST and copy it to `proffastpylot`
3. Create a virtual environment in python
4. Install PROFFASTpylot
5. Resulting folder structure
6. Test the installation by running an example dataset
7. Getting Updates
8. Contribution Notes



## 1. Download the PROFFASTpylot repository

**We recommend downloading the files using [git](https://www.git-scm.com).**   

It will make future updates easier.


### Clone the PROFFASTpylot repository using git

```
git clone https://gitlab.eudat.eu/coccon-kit/proffastpylot.git
```
A folder `proffastpylot` containing all program files will be created.


### Download the PROFFASTpylot repository as a zip file

Alternatively download and unpack the zip file 
https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/archive/master/proffastpylot-master.zip

Extracting it will create the folder `proffastpylot`.



## 2. Get PROFFAST and copy it to `proffastpylot`

### Download PROFFAST
Download PROFFAST Version 2.2 from the KIT website:  
https://www.imk-asf.kit.edu/english/3225.php

**For Linux users**: Run the installation script to create the executables. 
```
bash install_proffast_linux.sh
```
For Windows users, the executables are already provided.


### Copy the PROFFAST directory into `proffastpylot`

Copy the `prf` folder that was extracted from the zip file into `proffastpylot`.

## 3. Create a virtual environment in python

We recommend using a virtual environment (venv) to avoid conflicts between any other packages or Python modules.

1. (Only first time) Navigate to the `proffastpylot` folder using a terminal.
2. (Only first time) Enter `python -m venv prf_venv
   This command will create a folder named `prf_venv` which contains the virtual environment
3. Activate the virtual environment with
   - *Windows PowerShell:* `.\prf_venv\Scripts\Activate.ps1`
   - *Windows Commandline:* `.\prf_venv\Scripts\activate`
   - *Linux:* `source prf_venv/bin/activate`
4. To deactivate run `deactivate`

Note that all packages to be installed with `pip install` will only affect the virtual environment and not the local Python installation.  
In case of a problem, take a look at the [Troubleshooting](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/docs/2-5_troubleshooting.md) page.

You need to activate the virtual environment bevore each run of PROFFASTpylot by executing the command in step 4,
the other steps need to be executed only the first time.


## 4. Install the PROFFASTpylot repository

Activate the virtual environment (see above).

Navigate to `proffastpylot` and enter
```
pip install --editable .
```

To test the installation execute the `run.py` script. For details see [usage.md](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/docs/1-2_usage.md).

## 5. Resulting folder structure

If you follow exactly the installation guide your folder structure should look like the following:
```
proffastpylot
├── prf_venv
│   ├── ...
├── docs
│   ├── ...
├── example
│   ├── input_sodankyla_example.yml
│   ├── log_type_pressure.yml
│   └── run.py
├── prf
│   ├── docs
│   ├── inp_fast
│   ├── inp_fwd
│   ├── preprocess
│   ├── source
│   ├── out_fast
│   └── wrk_fast
├── prfpylot
│   ├── ...
└── setup.py
```

## 6. Test the installation by running an example dataset
To test the installation we provide example raw data and a reference result file to compare the file to.
The example can be executed by navigating to the example folder and execute `python run.py`
(please ensure that your virtual environment is activated).   
When first running the program it will ask you to download the exampe file data to your local computer.

After the run is complete, please compare your results to the data given in `example\Reference_Output_Example_Sodankyla.csv`.
The deviations should be less than 0.1 ppm for XCO2, 0.1 ppb for XCH4 and 0.1 ppb for XCO.

## 7. Getting Updates

If you used git during installation, you can easily get updates by entering

```
git pull
```
in a `git bash` or in a Terminal in your `proffastpylot` folder. This command will download all available updates.
If you downloaded PROFFASTpylot as zip file, you need to redo all steps of this installation script.

## 8. Contribution Notes

If you want to share a contribution to PROFFASTpylot please check our `dev` branch first (by `git checkout dev`) if your change still fits to the latest developments. Afterwards you are welcome to create a merge request or contact us via email about your suggestion.