# Installation

_For using prfPylot you need Python 3.7 or newer._

## Content

1. Get PROFFAST
2. Create a virtual environment for Python
3. Clone and install the prfPylot repository
4. Copy the PROFAST directory into prfPylot

## 1. Get PROFFAST

Download and install an up-to-date version of PROFFAST.

Clone the PROFFAST Repository.
```
git clone https://git.scc.kit.edu/imk-asf-bod/proffast.git
```

Alternatively you can also download and unpack the zip file 
https://git.scc.kit.edu/imk-asf-bod/proffast/-/archive/main/proffast-main.zip

**For Linux users**: Run the installation script to create the executables.  
```
./install_proffast_linux.sh
```
For Windows users, the executables are already provided.

## 2. Create a virtual environment in python

We recommend using a virtual environment (venv) to avoid conflicts between any other packages or Python modules.

1. Create a new folder for your virtual environment (e.g.
   `my_virtual_environments`)
2. Navigate to this folder using a terminal
3. Enter `python -m venv prf_venv`
   This command will create a folder named `prf_venv` which contains the virtual
   environment
4. Activate the virtual environment with
   - *Windows PowerShell:* `.\prf_venv\Scripts\Activate.ps1`  
   - *Windows Commandline:* `.\prf_venv\Scripts\activate` 
   - *Linux:* `source ./prf_venv/bin/activate`

Note that all packages to be installed with `pip install` will only affect the virtual environment and not the local Python installation.

In case of a problem, take a look at the [Troubleshooting](https://git.scc.kit.edu/cw4643/prfpylot/-/blob/master/docs/troubleshooting.md) page.


## 3. Clone and install the prfPylot repository

### Clone the prfpylot repository
```   
git clone git@git.scc.kit.edu:cw4643/prfpylot.git
```
A folder `prfpylot` containing all program files will be created.

Alternatively download and unpack the zip file 
https://git.scc.kit.edu/cw4643/prfpylot/-/archive/master/prfpylot-master.zip


### Install prfPylot using pip
Activate the virtual environment (see above).

Navigate to `prfpylot` and enter
```
pip install --editable .
```


## 4. Copy PROFFAST directory into prfPylot

Copy the PROFFAST directory into `prfpylot` and rename it to `prf`.

**For Linux Users**: Instead copying the directory you can create a symlink with e.g.
```
cd prfpylot
ln -s ../proffast prf
```
