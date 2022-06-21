import os
from os import path
from sys import argv
import argparse
cmake_data = ['cmake_minimum_required(VERSION 3.10)']



parser=argparse.ArgumentParser(prog='genproj')

parser.add_argument('--Name', help='Set the project name', action='store')
parser.add_argument('--Dir', help='Set the project folder', action='store')
parser.add_argument('--Type', help='Specify if this is C or C++ project', action='store')
parser.add_argument('--Output', help='Name the compilition output', action='store')
parser.add_argument('--Entry', help='Name the entrypoint (file containing main)', action='store')
parser.add_argument('--OutDir', help='Name the compilition output directory', action='store')
parser.add_argument('--LibDir', help='Name the compilition output for shared objects', action='store')
parser.add_argument('--BuildDir', help='Name the directory for building the project', action='store')
parser.add_argument('--SourceDir', help='Name the source directory', action='store')
parser.add_argument('--CC',  help='Set the C compiler', action='store')
parser.add_argument('--CCxx', help='Set the C++ compiler', action='store')
parser.add_argument('--CFlags', help='Set C compiler flags', action='store')
parser.add_argument('--Libs', help='Set libraries to link to', action='store')
parser.add_argument('--CxxFlags', help='Set C++ compiler flags', action='store')
parser.add_argument('--Debug', help='Set flags for the debug build', action='store')
parser.add_argument('--Release', help='Set flags for the release build', action='store')
parser.add_argument('--Include', help='Directories to include', action='store')

args = parser.parse_args()

if args.CC:
    cmake_data.append(f'set(CMAKE_C_COMPILER {args.CC})')
else:
    cmake_data.append(f'set(CMAKE_C_COMPILER gcc)')

if args.CCxx:
    cmake_data.append(f'set(CMAKE_CXX_COMPILER {args.CCxx})')
else:
    cmake_data.append(f'set(CMAKE_CXX_COMPILER g++)')

if args.CFlags:
    cmake_data.append(f'set(CMAKE_C_FLAGS {args.CFlags})')

if args.CxxFlags:
    cmake_data.append(f'set(CMAKE_CXX_FLAGS {args.CxxFlags})')

if args.Libs:
    cmake_data.append(f'set(CMAKE_C_FLAGS {args.CFlags})')

cmake_data.append(f'set(CMAKE_CXX_FLAGS_DEBUG "-g -ggdb3 -Og")')
cmake_data.append(f'set(CMAKE_C_FLAGS_DEBUG "-g -ggdb3 -Og")')
cmake_data.append(f'set(CMAKE_CXX_FLAGS_RELEASE "-O2")')
cmake_data.append(f'set(CMAKE_C_FLAGS_RELEASE "-O2")')

# Default name is Hello for now
project_name = args.Name if args.Name else 'Example'

# Default project dir is just current directory
project_dir = args.Dir if args.Dir else project_name.lower()

# C is default project type
project_type = args.Type if args.Type else 'C'
# Default executable is lower cased project name
exe_name = args.Output if args.Output else f'{project_name.lower()}'
# Entry default main.c/c++
entry_name = args.Entry if args.Entry else f'main.{project_type.lower()}'
# Output default folder is /bin
bin_dir = args.OutDir if args.OutDir else 'bin'
# Libraries default folder is /lib
lib_dir = args.LibDir if args.LibDir else 'lib'
# Source files default folder is /src
src_dir = args.SourceDir if args.SourceDir else 'src'
# Build directory defaults to /build
build_dir = args.BuildDir if args.BuildDir else 'build'
# .h/.hpp files go into /include by default
include_dir = args.Include if args.Include else 'include'


cmake_data.append(f'project({project_name})')

cmake_data.append(f'add_executable({exe_name} {src_dir}/{entry_name})')

# Tell cmake to put our files where we want them
cmake_data.append(f'''
set_target_properties( {exe_name}
    PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${{CMAKE_SOURCE_DIR}}/{lib_dir}"
    LIBRARY_OUTPUT_DIRECTORY "${{CMAKE_SOURCE_DIR}}/{lib_dir}"
    RUNTIME_OUTPUT_DIRECTORY "${{CMAKE_SOURCE_DIR}}/{bin_dir}"
)''')

cmake_data.append(f'set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${{CMAKE_SOURCE_DIR}}/{lib_dir}")')
cmake_data.append(f'set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${{CMAKE_SOURCE_DIR}}/{lib_dir}")')
cmake_data.append(f'set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${{CMAKE_SOURCE_DIR}}/{bin_dir}")')

# More argument parsing
if args.Include:
    cmake_data.append(f'include_directories({args.Include})')

cmake_data.append(f'include_directories({include_dir})')
cmake_data.append(f'add_subdirectory({src_dir})')

if args.Libs:
    cmake_data.append(f'target_link_libraries({project_name} PUBLIC {args.Libs})')

# used to create directories. IF they do not already exist.
def mkdirs_if_not_exists(names: iter):
    # If a directory does exist, we raise an exception
    if path.exists(project_dir):
        raise(IsADirectoryError(f'Directory already exists {path.abspath(project_dir)}!'))

    if not path.exists(project_dir):
        os.mkdir(project_dir)
        for name in names:
            os.mkdir(path.join(project_dir, name))
    
    else:
        os.makedirs([name for name in names if not path.exists(name)])
        
        
# Create our project directories
mkdirs_if_not_exists([src_dir, lib_dir, bin_dir, build_dir, include_dir])

with open(f'{project_dir}/CMakeLists.txt','w+') as f:
    f.write('\n'.join(cmake_data))

with open(f'{path.join(project_dir,src_dir)}/CMakeLists.txt', 'w+') as f:
    f.write('')

with open(f'{project_dir}/build.sh', 'w+') as f:
    f.write('''#! /bin/bash
cd build
if [ "$1" = "Clean" ] || [ "$2" = "Clean" ] 
then
    rm CMakeCache.txt
fi

if [ $1 == "Debug" ]
then
    cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -DCMAKE_BUILD_TYPE=Debug
elif [ $1 == "Release" ]
then
    cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -DCMAKE_BUILD_TYPE=Release
else
    cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=1
fi
make
cd ..''')

os.system(f'chmod +x {project_dir}/build.sh')

with open(f'{path.join(project_dir, src_dir)}/main.c', 'w') as f:
    f.write('''#include <stdio.h>

int main(int argc, char **argv){
    printf("Did it work?\\n");
    return 0;
}
    ''')