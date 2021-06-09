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



## Implement basic MDI support

We will now begin to implement support for MDI_MC_Demo to act as an MDI engine.
When MDI Mechanic previously executed the `build_engine` step, it cloned the MDI_MC_Demo repository into `build/MDI_MC_Demo`.
Open the repository's Python code, which is located at `build/MDI_MC_Demo/MDI_MC_Demo/MDI_MC_Demo.py`.

We need to add `import mdi` to the file's import statements.
Later on, we will also need access to `sys`, so the full set of import statements should be:
```Python
from mpi4py import MPI
import numpy as np
import mdi
import sys
```

MDI engines are expected to accept `-mdi` command-line option, which allows the end-user to configure various MDI runtime options (*i.e.*, whether MDI will communicate between codes using MPI or TCP/IP sockets, *etc.*).
Modify the beginning of the `MCSimulation` initialization function to receive the `-mdi` command-line option:
```Python
class MCSimulation:
    def __init__(self):

        # Receive the -mdi option
        mdi_options = None
        self.use_mdi = False
        for iarg in range( len(sys.argv) ):
            if sys.argv[iarg] == "-mdi" or sys.argv[iarg] == "--mdi":
                if len(sys.argv) > iarg + 1:
                    mdi_options = sys.argv[iarg+1]
                    self.use_mdi = True
                else:
                    raise Exception('Argument to -mdi option was not provided')
```

Immediately after these lines, initialize the MDI Library:
```Python
        if self.use_mdi:
            mdi.MDI_Init(mdi_options)
```

Under the comment that reads `MPI Initialization` is the following line:
```Python
    world_comm = MPI.COMM_WORLD
```
Replace this line with:
```Python
        self.world_comm = MPI.COMM_WORLD
        if self.use_mdi:
            self.world_comm = mdi.MDI_MPI_get_world_comm()
```
This ensures that the MDI_MC_Demo engine will use the correct MPI communicator if the MDI communication is handled via MPI.

It is now necessary for the engine to establish a connection with the external driver.
At the end of the `MCSimulation` initialization function, add the following code:
```Python        
        self.mdi_comm = None
        if self.use_mdi:
            # Establish a connection with an external driver
            self.mdi_comm = mdi.MDI_Accept_communicator()

            # Set the MDI exit flag
            self.mdi_exit_flag = False
```

We now need to write code that will enable MDI_MC_Demo to receive and correctly respond to commands from the driver.
Add the following function to the `MCSimulation` class:
```Python
    def mdi_node(self, node_name):

        # Main MDI loop
        while not self.mdi_exit_flag:
            # Receive a command from the driver
            self.command = mdi.MDI_Recv_command(self.mdi_comm)

            # Broadcast the command to all ranks
            self.command = world_comm.bcast(self.command, root=0)

            # Respond to the received command
            if self.command == "EXIT":
                self.mdi_exit_flag = True
            else:
                # The received command is not recognized by this engine, so exit
                raise Exception('MDI Engine received unrecognized command: ' + str(self.command))
```

Finally, we will call this code immediately before the Monte Carlo simulation begins.
At the very beginning of the `MCSimulation` `run` function, insert a call to the `mdi_node` function:
This should look like:
```Python
        if use_mdi:
            self.mdi_node("@DEFAULT")
            if self.command == "EXIT":
                return
```

That's everything we need for basic MDI functionality.
Before MDI Mechanic can test our MDI implementation, we need to tell MDI Mechanic how to run MDI_MC_Demo as an MDI engine.
For a normal user, this is done simply by launching MDI_MC_Demo with an additional `-mdi` command-line option.
For example:
```
python MDI_MC_Demo.py -mdi "-name engine -role ENGINE -method TCP -hostname localhost -port 8021"
```
MDI Mechanic sets the argument to the `-mdi` option to an environment variable called `MDI_OPTIONS`.
Provide MDI Mechanic with an MDI-enabled launch script by modifying the `engine_tests` field in `mdimechanic.yml` to the following:
```
engine_tests:
  # Provide at least one example input that can be used to test your code's MDI functionality
  - script:
      -	cd build/MDI_MC_Demo/MDI_MC_Demo
      -	python MDI_MC_Demo.py -mdi "${MDI_OPTIONS}"
```

Now execute `mdimechanic report` in the directory where `mdimechanic.yml` is located.
The first few lines of output should be:
```
Starting a report
Success: Able to verify that the engine was built
Success: Engine passed minimal MDI functionality test.
Success: Engine errors out upon receiving an unsupported command.
```

## Add support for the `<NATOMS`, `<COORDS`, `<CELL`, and `<CELL_DISPL` commands

We will now edit the `mdi_node` function to add support for the `<NATOMS` MDI command.
This command requires that the engine send the total number of atoms in its system to the driver.
We will need to add functionality for `MDI_MC_Demo` to do this as part of the `if ... else` clause that is labeled with the comment `Respond to the received command`
Add the following lines after the `command == "EXIT"` case:
```Python
            elif command == "<NATOMS":
                mdi.MDI_Send(self.num_particles, 1, MDI_INT, self.mdi_comm)
```
The full `if ... else` clause should look like:
```Python
            # Respond to the received command
            if self.command == "EXIT":
                self.mdi_exit_flag = True
            elif command == "<NATOMS":
                mdi.MDI_Send(self.num_particles, 1, MDI_INT, self.mdi_comm)
            else:
                # The received command is not recognized by this engine, so exit
                raise Exception('MDI Engine received unrecognized command: ' + str(self.command))
```

Supporting the `<COORDS` command follows a similar process, except that we must also convert `MDI_MC_Demo`'s internal coordinates from Lennard-Jones reduced units to atomic units, which are used by MDI.
The following code will accomplish this:
```Python
            elif command == "<COORDS":
                conversion_factor = self.sigma * MDI_Conversion_factor("meter","atomic_unit_of_length")
                mdi_coords = conversion_factor * self.coordinates
                mdi.MDI_Send(mdi_coords, 3 * self.num_particles, MDI_DOUBLE, self.mdi_comm)
```

For the `<CELL` command, the engine must send its full set of cell vectors to the driver.
```Python
            elif command == "<CELL":
                conversion_factor = self.sigma * MDI_Conversion_factor("meter","atomic_unit_of_length")
                mdi_box_length = conversion_factor * self.box_length
                cell = [ mdi_box_length, 0.0, 0.0, 0.0, mdi_box_length, 0.0, 0.0, 0.0, mdi_box_length ]
                mdi.MDI_Send(cell, 9, MDI_DOUBLE, self.mdi_comm)
```

The `<CELL_DISPL` command requires that the engine send the driver a vector that corresponds to the displacement of the periodic cell's origin.
For `MDI_MC_Demo`, the origin of the cell is at `[-0.5*self.box_length, -0.5*self.boxlength, -0.5*self.box_length]`.
The following code will correctly respond to the `<CELL_DISPL` command:
```Python
            elif command == "<CELL_DISPL":
                conversion_factor = self.sigma * MDI_Conversion_factor("meter","atomic_unit_of_length")
                mdi_box_length = conversion_factor * self.box_length
                cell_displ = [ -0.5*mdi_box_length, -0.5*mdi_box_length, -0.5*mdi_box_length ]
                mdi.MDI_Send(cell_displ, 3, MDI_DOUBLE, self.mdi_comm)
```

If you rerun `mdimechanic report`, the output should indicate that all four of the above commands are now working.



### Copyright

Copyright (c) 2021, Taylor Barnes


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.5.
