# Installation

## Content

1. Get PROFFAST
2. Make a virtual environment in python
3. Clone and install the prfPylot repository
4. Copy the PROFAST directory into prfPylot

## 1. Get PROFFAST

First, download and install an up-to-date version of PROFFAST.

Clone the PROFFAST Repository.   
`git clone https://git.scc.kit.edu/imk-asf-bod/proffast.git`

Alternatively you can also download it as a zip file:    
`https://git.scc.kit.edu/imk-asf-bod/proffast/-/archive/main/proffast-main.zip`

**For Linux Users**: Run the script installation script to create the executables.  
`./install_proffast_linux.sh`  
For Windows users, the executables are already provided.

## 2. Create a virtual environment in python
We recommend to use prfPylot in a virtual environment (venv).
This ensures that prfPylot works conflict-free with any other packages.
Here it is explained how a virtual environment can be created.
This tutorial assumes that python3.x with x>6 is installed.


1. Create a new folder where you want to store the prfPylot and name it e.g.
   prfpylot.
2. Navigate to this folder using a terminal.
3. Enter `python -m venv .venv`
   This command will create a folder named '.venv' which contains the virtual
   environment. The name '.venv' can be replaced by anything you would like to.
4. To start the virtual environment use the following command in dependence of
   your operating system and shell you are using:
   - *Windows PowerShell:* `.\.venv\Scripts\Activate.ps1`  
   - *Windows Commandline:* `.\.venv\Scripts\activate` 
   - *Linux:* `source ./.venv/bin/activate`
5. Now you can use python as you are used to. However all packages you are
   going to install via `pip install` do only affect the venv and not your
   local python installation. Hence this prevents you firstly
   from messing up your local installation and sencondly prfPylot runs without
   any version conflicts of any old installations. 


## 3. Clone and install the prfPylot repository

Clone the prfpylot repository to a folder you want it to be saved:   
`git clone git@git.scc.kit.edu:cw4643/prfpylot.git`

Alternatively it can be downloaded as a zip file and stored wherever you want:   
`https://git.scc.kit.edu/cw4643/prfpylot/-/archive/master/prfpylot-master.zip`


### Install prfPylot via pip:
1. If you are using a virtual environment activate it first
2. navigate to the folder you have chosen in the previous step and enter    
   `pip install --editable .`  

prfPylot is written with python3. We recommend using python >= 3.7.


## 4. Copy PROFFAST directory into prfPylot

Copy the PROFFAST directory into `prfpylot` and rename it to `prf`.

**For Linux Users**: Instead copying the directory you can create a symlink with e.g.
```
cd prfpylot
ln -s ../proffast prf
```
## 5. Troubleshooting

We have encountered some errors on machines with non-standard python setup.    
1. If you have several python installations, where some are not included to your
   PATH variable it might can happend that the creation of an virtual environment
   results in 
    `Error: [WinError 2] The system cannot find the file specified`.      
   In this case the a solution can be to give to full path to your python
   executable whilst creating the virtual environment:    
   `C:\path\to\your\python\python.exe -m venv MyVenv`
