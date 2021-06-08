MDI_MC_Demo
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/workflows/CI/badge.svg)](https://github.com/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/branch/master/graph/badge.svg)](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/branch/master)


A very basic Monte Carlo code intended to be used as part of an MDI engine tutorial.

# Overview

This code performs simple Monte Carlo simulations in which particles interact via a Lennard-Jones potential.
The purpose of this repository is to serve as the starting point for an MDI tutorial that demonstrates the process of implementing an MDI interface in an existing production code.  The full tutorial is provided later in this README file, in the Tutorial section.

# Tutorial

## Prerequisites

This tutorial will use [MDI Mechanic](https://github.com/MolSSI-MDI/MDI_Mechanic), which must be installed on your system:

```pip install mdimechanic```

MDI Mechanic uses Docker extensively, so you must also install Docker and launch Docker Desktop.
In order to more easily view the output from MDI Mechanic, it is recommended that you install an offline markdown viewer, such as `grip`:

```pip install grip```

## Start an MDI Mechanic project

Start an MDI Mechanic project with the following commands:

```
mkdir MDI_MC_Demo_Report
cd MDI_MC_Demo_Report
mdimechanic startproject --enginereport
```

This will add several new files to the `MDI_MC_Demo_Report` directory, including one called `mdimechanic.yml`.

## Configure the MDI Mechanic YAML file

The mdimechanic.yml file created in the previous step is used by MDI Mechanic to build your engine and to test and analyze its functionality as an MDI engine.
If you have used continuous integration (CI) testing services in the past, you will likely recognize many similarities between mdimechanic.yml and the YAML files that are often used by those services.
Open mdimechanic.yml in your favorite text editor, and you will see that MDI Mechanic pre-populated this file with a basic template.

This tutorial will go over each field in mdimechanic.yml in detail, but the following is a quick summary:

* **code_name:** The name of your code, which is used when printing out information.
* **image_name:** MDI Mechanic will create an Docker image, which will contain a highly portable environment that can be used to reproducibly build and run your engine. This field sets the name of the engine MDI Mechanic will create.
* **build_image:** This provides a script that is used to build the Docker image that MDI Mechanic builds. It corresponds to the steps required to prepare an environment with all of your engine's dependencies, and is comparable to a before_install step in some CI services.
* **build_engine:** This provides a script to build your engine. It is executed within the context of the Docker image built by MDI Mechanic, and is comparable to an install step in some CI services.
* **validate_engine:** This provides a script to verify that your engine has been built successfully. It is comparable to a script step in some CI services.
* **engine_tests:** This provides scripts used to test MDI functionality in your engine.

For now, just replace the value of `code_name` with the name of the engine (`MDI_MC_Demo`), and set the value of `image_name` to `mdi_mc_demo/mdi_report`

## Define the engine's dependencies using MDI Mechanic

This tutorial uses MDI Mechanic, which in turn runs your code within the context of a Docker image
In crude terms, you can think of an image as being a simulated duplicate of another computer, which has a different environment from yours (i.e. different installed libraries and system settings), and might be running an entirely different operating system.
The image created by MDI Mechanic is based on the Ubunto Linux distribution.
Starting from the basic Linux environment, MDI Mechanic installs some basic compilers (`gcc`, `g++`, and `gfortran`), an MPI library (`MPICH`), Python 3, and a handful of other dependencies (`make` and `openssh`).
To finish building the image, MDI Mechanic executes whatever script you've provided in the `build_image` section of `mdimechanic.yml`.

We must now fill out `build_image` with an appropriate script that installs any dependencies necessary to run the `MDI_MC_Demo` engine.
If you look at `MDI_MC_Demo/MDI_MC_Demo.py`, you will see that in requires both `mpi4py` and `numpy`:

```
from mpi4py import MPI
import numpy as np
```

We want both of these dependencies to be installed during the `build_image` step.
In addition, we should install the cmake and the MDI Library, as the engine will need it later.
Finally, we will want the image to have `git` installed, so that we can acquire a copy of the MDI_MC_Demo GitHub repository.
Modify the `build_image` step to read:
```
  build_image:
    - pip install mpi4py
    - pip install numpy
    - pip install cmake
    - pip install pymdi
    - apt-get update
    - apt-get install -y git
```

We can now check to see if MDI Mechanic is able to build the image by executing the following command, in the same directory where `mdimechanic.yml` is located:
```
mdimechanic build
```
This command may take a few minutes to execute, during which time Docker is working to build an image according to the instructions we gave it.
If everything worked correctly, you should see the following line printed out at the end:
```
Insert commands to build your engine code here
```
This line is printed by MDI Mechanic after it has built the image: specifically, after building the image, MDI Mechanic launches an instance of this image (*e.g.*, a container), and executes `build_engine` script in `mdimechanic.yml` **within that container**.
Our current `build_engine` script reads:
```
  build_engine:
    - echo "Insert commands to build your engine code here"
```
Unsurprisingly, when our new Docker container executes this script, it prints the line we saw at the end of the `mdimechanic build` execution.

## Build the engine using MDI Mechanic

We now need to modify the `build_engine` script so that it correctly acquires a clone of the MDI_MC_Demo Python package.
Because this engine is a Python script, it is not necessary to compile anything during the `build_image` step.
Modify the `build_engine` step to read:
```
  build_engine:
    - |
      if [ ! -d "build/MDI_MC_Demo" ]; then
        git clone https://github.com/MolSSI-MDI/MDI_MC_Demo.git build/MDI_MC_Demo
      fi
    - echo "Finished build_engine step"
```

Now if you execute `mdimechanic build` again, the output should end with:
```
Finished build_engine step
```

## Verify that the engine can be run

The primary purpose of MDI Mechanic is to portably validate MDI implementations.
You can run the full set of MDI Mechanic tests by executing the following command in the same directory where `mdimechanic.yml` is located:
```
mdimechanic report
```
The command will immediately return with the following error:
```
Exception: Error: Unable to verify that the engine was built.
```
The first test that MDI Mechanic performs is a test to confirm that the engine can be run successfully.
It does this by executing the script you provide in `validate_engine` in `mdimechanic.yml`.
We need to modify this script so that it corresponds to a basic test that confirms we are able to run the engine through MDI Mechanic.
The script should not test any MDI-specific functionality - it should only confirm that we can run MDI_MC_Demo.

Modify the `validate_engine` script so that it reads:
```
  validate_engine:
    - cd build/MDI_MC_Demo/MDI_MC_Demo
    - python MDI_MC_Demo.py
```
Now execute `mdimechanic report` again.
The output should indicate that MDI Mechanic was able to execute the `validate_engine` step successfully, but that it also found that MDI_MC_Demo lacks minimal MDI functionality:
```
Starting a report
Success: Able to verify that the engine was built
...
Exception: Error: Engine failed minimal MDI functionality test.
```
This is expected, since we have not yet begun to implement MDI support in MDI_MC_Demo.





### Copyright

Copyright (c) 2021, Taylor Barnes


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.5.
