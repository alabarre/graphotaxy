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
#!/bin/bash
#
# Install the Glasgow Subgraph Solver locally (outside of the project tree).
# Binaries will be installed in ~/.local/bin by default.
#

set -e

INSTALL_DIR="$HOME/.local/bin"
GSS_DIR="glasgow-subgraph-solver"
GSS_REPO="https://github.com/ciaranm/glasgow-subgraph-solver.git"

echo "This script will download and build the Glasgow Subgraph Solver."
echo "It is licensed separately under its own terms."
echo "It may have restrictions (e.g. non-commercial use)."
echo "See: https://github.com/ciaranm/glasgow-subgraph-solver"
echo

read -p "Continue? [y/N] " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Aborted."
    exit 1
fi

echo
echo "+------------------------------------------------+"
echo "| Cloning the Glasgow Subgraph Solver repository |"
echo "+------------------------------------------------+"
echo

if [[ -d "$GSS_DIR" ]]; then
    answer=""
    while [[ "$answer" != "e" && "$answer" != "s" && "$answer" != "a" ]]; do
        read -p "Directory $GSS_DIR exists: (e)rase, (s)kip clone, or (a)bort? [e/s/a] " answer
    done

    if [[ "$answer" == "e" ]]; then
        rm -rf "./$GSS_DIR"
        git clone "$GSS_REPO"
    elif [[ "$answer" == "a" ]]; then
        echo "Aborted."
        exit 1
    fi
else
    git clone "$GSS_REPO"
fi

echo
echo "+-----------------------+"
echo "| Checking dependencies |"
echo "+-----------------------+"
echo

packages_to_install=()

# Debian-based systems only (best effort)
if command -v dpkg &> /dev/null; then
    devlibs=(libgmp-dev)
    for lib in "${devlibs[@]}"; do
        if ! dpkg -s "$lib" &> /dev/null; then
            packages_to_install+=("$lib")
        fi
    done
fi

binaries=(cmake gcc)
for bin in "${binaries[@]}"; do
    if ! command -v "$bin" &> /dev/null; then
        packages_to_install+=("$bin")
    fi
done

if (( ${#packages_to_install[@]} )); then
    echo "Missing dependencies: ${packages_to_install[*]}"
    read -p "Install them automatically (Debian/Ubuntu)? [y/N] " install_deps

    if [[ "$install_deps" == "y" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y "${packages_to_install[@]}"
        else
            echo "Automatic install not supported on this system."
            echo "Please install dependencies manually and rerun."
            exit 1
        fi
    else
        echo "Please install dependencies manually and rerun."
        exit 1
    fi
else
    echo "All required dependencies are installed."
fi

echo
echo "+---------------------------------------------------+"
echo "| Compiling the Glasgow Subgraph Solver             |"
echo "+---------------------------------------------------+"
echo

cd "$GSS_DIR"
cmake -S . -B build
cmake --build build

echo
echo "+------------------------------+"
echo "| Installing binaries          |"
echo "+------------------------------+"
echo

mkdir -p "$INSTALL_DIR"

cd build
installed_any=false

for file in *; do
    if [[ -f "$file" && -x "$file" ]]; then
        cp "$file" "$INSTALL_DIR/"
        echo "Installed: $file -> $INSTALL_DIR"
        installed_any=true
    fi
done

if [[ "$installed_any" = false ]]; then
    echo "Warning: no executable files found."
fi

echo
echo "+---------------------------------------------+"
echo "| Cleaning up source directory                |"
echo "+---------------------------------------------+"
echo

cd ..
cd ..
rm -rf "./$GSS_DIR"

echo
echo "+-------+"
echo "| Done. |"
echo "+-------+"
echo

# PATH reminder
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo
    echo "  $INSTALL_DIR is not in your PATH."
    echo "Add the following line to your shell config (~/.bashrc, ~/.zshrc):"
    echo
    echo "export PATH=\"$INSTALL_DIR:\$PATH\""
fi
