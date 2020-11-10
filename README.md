# G2_artifact_eval

## Introduction
This repository is the guide for evaluating our CGO2021 paper, "Techniques for Compiling Graphs Algorithms for GPUs". This guide has steps for cloning, compiling and executing the implmentation of the compiler framework G2 which is built on top of the [GraphIt DSL compiler](https://graphit-lang.org/). 
This guide has two parts -
  - Part 1: Reproducing Figure 3. in the paper to demonstrate that the compiler can generate very different optimized code for different schedules
  - Part 2: Reproducing the G2 columns for all the applications and graphs from Table 7 to demonstrate the performance of the code generated from the G2 compiler

Since Table 7 shows the performance numbers when run on the NVIDIA-Tesla V-100 GPU, the exact execution times you will get in Part 2 will depend on the actual GPU you use. If you do not have access to the same GPU, we have provided access to our system with this GPU in our artifact evaluation submission. 
If you use any other GPU the schedules might have to be tuned to get the best performance for the GPU. 

## Requirements
We expect you to run the artifact evaluation on a Linux system with atleast 40GBs of space. Following are the software requirements for each of the parts

### Part 1
Since part 1 only demonstrates the different code generated for different schedules, this part does *NOT* require an NVIDIA GPU or CUDA to be installed. The only software requirements are - 

 - cmake (>= 3.5.1)
 - CXX compiler (like g++ >= 5.4.0)
 - python3 
 - make
 - bash
 - git

### Part 2
Part 2 demonstrates the performance of these applications on the actual GPU. Ideally we require an NVIDIA Tesla V-100 for best results, but other NVIDIA GPUs would also work (the actual performance numbers would be different in that case). 

 - NVIDIA GPU (Pascal generation or better, preferred NVIDIA Tesla V-100 32 GB, access to our machine provided in the artifact evaluation submission). 
 - CUDA SDK (>= 9.0)


## How to run 

### Cloning
We will start by cloning this repository on the evaluation system using the following command - 

    git clone --recursive https://github.com/AjayBrahmakshatriya/G2_artifact_eval.git

If you have already cloned this repository without the `--recursive` command you can get the submodules by running the following commands. Otherwise you can directly proceed to Building G2.

   git submodule init
   git submodule update
   
### Building G2
Start by navigating to the `G2_artifact_eval` directory. We will first build the G2 compiler by running the following commands from the repo's top level directory - 

    cd graphit
    mkdir build
    cd build
    cmake ..
    make
    
If no errors are reported, the G2 compiler is built correctly and you can navigate back to the repository's top level directory and proceed to "Obtaining the datasets"

### Obtaining the datasets
The datasets are only requried for Part 2. So if you are planning to not run Part 2 or are planning to run Part 2 on a different system, you can skip this step for now. 

There are two ways of obtaining the datasets. If you are running this artifact evaluation on the system we have provided access to, you can quickly fetch all the data set files by running the following commands in the top level directory - 

    cd datasets
    make local
    
If everything succeeds, the dataset should be soft-linked into this directory and you can verify that by running the `ls` command. You can now proceed to the next step. If the command reports the error 

> You are not running this command on the right host. Please use `make dataset` instead

it means that you are not running the artifact evaluation on our system and you should use the other method for downloading the datasets

If you are running the artifact evaluation on your own system, you can obtain the datasets by running the following commands in the top level directory - 

    cd datasets
    make dataset
    
This step will take some time, because it downloads and uncompresses all the datasets (~9.8 GBs). After the command succeeds, you can verify that the files are downloaded by running the `ls` command. 

### Running Part 1
With the G2 compiler built, you can run the Part 1 to generate the code as show in Figure 3. You can start by running the following command in the top level directory of the repository - 

    python3 gen_fig3.py


When running this command, the program will prompt for a few options like paths to where the G2 compiler is built. If you have followed the above steps, you can simply press enter and choose the default options shown in `[]`. 

This command should take about 5 mins to run and if it doesn't report any errors, the appropriate files have been generated. Notice the above commands also prints all the commands that were executed to generate the output files. 

## Evaluating related works
