#!/bin/bash
#
# An installation script for the Glasgow Clique and Subgraph solvers, which compiles them and
# copies them where graphotaxy needs them. Compilation is mandatory.
#
# Do not move this script, it is exactly where it is supposed to be.
#
# Usage: ./install_gss.sh
#
# Copyright (C) 2025-2026
#
# Author: Anthony Labarre
echo "+------------------------------------------------+"
echo "| Cloning the Glasgow Subgraph Solver repository |"
echo "+------------------------------------------------+"
echo
gss_git_address=https://github.com/ciaranm/glasgow-subgraph-solver.git
if [[ -d glasgow-subgraph-solver ]]
then
    echo "Error: target directory glasgow-subgraph-solver already exists"
    while [[ $answer != "e" && $answer != "s" && $answer != "a" ]]
    do
        read -p "Do you want to (e)rase it and retry, (s)kip this step, or (a)bort? [e/s/a] " -r answer
    done
    if [[ $answer == "e" ]]
    then
        rm -rf glasgow-subgraph-solver
        git clone $gss_git_address
    elif [[ $answer == "a" ]]
    then
        echo
        echo "OK, aborting."
        exit
    fi
else
    git clone $gss_git_address
fi

echo
echo "+-----------------------+"
echo "| Checking dependencies |"
echo "+-----------------------+"
echo
# TODO assuming a Ubuntu-like platform for now (specifically Debian, since it's
# what I use); if that doesn't work for you, get in touch so I can improve this
# script
# TODO /etc/os-release tells us what we're actually running
# find out if necessary packages are installed
declare -a packages_to_install=()
devlibs=(libgmp-dev)
for libname in "${devlibs[@]}"
do
    present=$(dpkg --get-selections | grep "$libname")
    if [[ -z $present ]]
    then
        packages_to_install+=("$libname")
    fi
done
binnames=(cmake gcc)
for path in "${binnames[@]}"
do
    location=$(which "$path")
    if [[ -z $location ]]
    then
        packages_to_install+=("$path")
    fi
done
if (( ${#packages_to_install[@]} ))
then
    echo
    echo "You are missing the following dependencies:" "${packages_to_install[@]}"
    echo "I can install them for you, or you can abort, install them yourself, then launch me again"
    echo
    while [[ $answer != "e" && $answer != "s" && $answer != "a" ]]
    do
        read -p "Do you want to (i)nstall dependencies or (a)bort? [i/a] " -r answer
    done
    if [[ $answer == "i" ]]
    then
        sudo apt install "${packages_to_install[@]}"
    elif [[ $answer == "a" ]]
    then
        echo
        echo "OK, aborting."
        exit
    fi
else
    echo "Everything required to build the Glasgow tools is installed."
fi

echo
echo "+---------------------------------------------------+"
echo "| Compiling the Glasgow Clique and Subgraph solvers |"
echo "+---------------------------------------------------+"
echo
cd glasgow-subgraph-solver
cmake -S . -B build
cmake --build build

echo
echo "+---------------------------------------------------+"
echo "| Copying binaries to the graph_recognition package |"
echo "+---------------------------------------------------+"
echo
cd build
for file in $(ls)
do
    if [[ -f $file && -x file ]]
    then
        cp $file ../../graph_recognition
    fi
done

echo
echo "+-------------------------------------------------------------------+"
echo "| Removing the glasgow_subgraph_solver directory (no longer useful) |"
echo "+-------------------------------------------------------------------+"
echo
cd ../../
rm -rf glasgow-subgraph-solver/

echo
echo "+-------+"
echo "| Done. |"
echo "+-------+"
echo
