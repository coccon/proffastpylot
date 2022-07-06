# Installation

**For using PROFFASTpylot you need Python 3.7 or newer.**

## Content

1. Download the PROFFASTpylot repository
2. Get PROFFAST and copy it to proffastpylot
3. Create a virtual environment in python
4. Install PROFFASTpylot
5. Resulting folder structure



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
Download and install an up-to-date version of PROFFAST.
It can be found on the KIT website:  
https://www.imk-asf.kit.edu/english/3225.php

**For Linux users**: Run the installation script to create the executables. 
```
bash install_proffast_linux.sh
```
For Windows users, the executables are already provided.


### Copy the PROFFAST directory into `proffastpylot`

Copy the PROFFAST directory into `proffastpylot` and rename it to `prf`.

## 3. Create a virtual environment in python

We recommend using a virtual environment (venv) to avoid conflicts between any other packages or Python modules.

2. Navigate to the `proffastpylot` folder using a terminal.
3. Enter `python -m venv prf_venv`
   This command will create a folder named `prf_venv` which contains the virtual environment
4. Activate the virtual environment with
   - *Windows PowerShell:* `.\prf_venv\Scripts\Activate.ps1`
   - *Windows Commandline:* `.\prf_venv\Scripts\activate`
   - *Linux:* `source ./prf_venv/bin/activate`
5. To deactivate run `deactivate`

Note that all packages to be installed with `pip install` will only affect the virtual environment and not the local Python installation.  
In case of a problem, take a look at the [Troubleshooting](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/docs/troubleshooting.md) page.

You need to activate the virtual environment bevore each run of PROFFASTpylot by executing the command in step 4,
the other steps need to be executed only the first time.


## 4. Install the PROFFASTpylot repository

Activate the virtual environment (see above).

Navigate to `proffastpylot` and enter
```
pip install --editable .
```

To test the installation execute the `run.py` script. For details see [usage.md](https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/blob/master/docs/usage.md).

## 5. Resulting folder structure

If you follow exactly the installation guide your folder strucutre should look like the following:
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