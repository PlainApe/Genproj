import os
import os.path
from sys import argv
import argparse
cmake_data = ['cmake_minimum_required(VERSION 3.10)']



parser=argparse.ArgumentParser(prog='genproj')

parser.add_argument('--Name', help='Set the project name', action='store')
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

project_name = args.Name if args.Name else 'Hello'
project_type = args.Type if args.Type else 'C'
exe_name = args.Output if args.Output else f'{project_name.lower()}'
entry_name = args.Entry if args.Entry else f'main.{project_type.lower()}'
bin_dir = args.OutDir if args.OutDir else 'bin'
lib_dir = args.LibDir if args.LibDir else 'lib'
src_dir = args.SourceDir if args.SourceDir else 'src'
build_dir = args.BuildDir if args.BuildDir else 'build'
include_dir = args.Include if args.Include else 'include'
cmake_data.append(f'project({project_name})')

cmake_data.append(f'add_executable({exe_name} {src_dir}/{entry_name})')


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

if args.Include:
    cmake_data.append(f'include_directories({args.Include})')

cmake_data.append(f'include_directories({include_dir})')
cmake_data.append(f'add_subdirectory({src_dir})')

if args.Libs:
    cmake_data.append(f'target_link_libraries({project_name} PUBLIC {args.Libs})')

def mkdirs_if_not_exists(names):
    for name in names:
        if not (os.path.exists(name)): 
            os.makedirs(name)
        
        

mkdirs_if_not_exists([f'{src_dir}', f'{lib_dir}', f'{bin_dir}', f'{build_dir}', f'{include_dir}'])

with open('CMakeLists.txt','w+') as f:
    f.write('\n'.join(cmake_data))

with open(f'{src_dir}/CMakeLists.txt', 'w+') as f:
    f.write('')

with open('build.sh', 'w+') as f:
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
