#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: Vivek Desai
Seneca ID: vdesai19
Semester: Fall 2024, OPS445ZAA
Date: 2024-12-01

The python code in this file is original work written by
"Student Name". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: Assignment 2A
'''

import argparse               
import os, sys                

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")   # Add argument for "human-readable" format, -H is used as -h is reserved for --help.
     
    parser.add_argument("program", type=str, nargs='?', help="If a program is specified, show memory use of all associated processes. Show only total use if not.")  # Optionally specify a program to show memory usage of associated processes.
    args = parser.parse_args()  # Parse and store command-line arguments
    return args  # Return the parsed arguments

def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    input_length = int(length * percent)  # Number of characters to represent the memory usage
    blank_length = length - input_length   # Calculate remaining blank space
    return '#' * input_length + ' ' * blank_length  # Return the graphical bar as a string

def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    with open('/proc/meminfo', 'r') as f:  # Open /proc/meminfo to read system memory info
        for line in f:
            if 'MemTotal' in line:  # Look for the line containing total memory
                return int(line.split()[1])  # Return the total memory value (in kB)
    return 0  # Return 0 if total memory information is not found

def get_avail_mem() -> int:
    "return total memory that is currently in use"
    with open('/proc/meminfo', 'r') as f:  # Open /proc/meminfo to read available memory info
        for line in f:
            if 'MemAvailable' in line:  # Look for the line containing available memory
                return int(line.split()[1])  # Return the available memory value (in kB)
    return 0  # Return 0 if available memory information is not found

def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"
    result = os.popen(f'pidof {app_name}').read().strip()  # Get process IDs (PIDs) of the app
    if result:
        return result.split()  # Return list of PIDs if found
    return []  # Return an empty list if no PIDs are found

def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    with open(f'/proc/{proc_id}/status', 'r') as f:  # Open the process status file for the given PID
        for line in f:
            if 'VmRSS' in line:  # Look for the resident memory (VmRSS) line
                return int(line.split()[1])  # Return the RSS memory value (in kB)
    return 0  

def bytes_to_human_r(kilobytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates memory units based on 1024
    suf_count = 0  # Initialize suffix counter (for MiB, GiB, etc.)
    result = kilobytes  # Start with kilobytes value
    while result > 1024 and suf_count < len(suffixes):  # Loop to convert units
        result /= 1024  # Convert to the next higher unit (e.g., MiB)
        suf_count += 1  # Increment the suffix counter
    str_result = f'{result:.{decimal_places}f} '  # Format the result with the specified decimal places
    str_result += suffixes[suf_count]  # Append the appropriate unit (KiB, MiB, etc.)
    return str_result  # Return the human-readable memory size

if __name__ == "__main__":  
    args = parse_command_args()  # Parse the command-line arguments
    total_memory = get_sys_mem()  # Get the total system memory
    
    if not args.program:  
        used_memory = total_memory - get_avail_mem()  # Calculate used memory (total - available)
        percent_used = used_memory / total_memory  # Calculate percentage of memory used
        graph = percent_to_graph(percent_used, args.length)  # Generate a graphical representation of memory usage
        
        if args.human_readable: 
            used_memory_str = bytes_to_human_r(used_memory)  # Convert used memory to human-readable format
            total_memory_str = bytes_to_human_r(total_memory)  # Convert total memory to human-readable format

            
            print(f"Memory         [{graph}| {int(percent_used * 100)}%] {used_memory_str}/{total_memory_str}")   # Output the memory usage with human-readable sizes
        else:
            
            print(f"Memory         [{graph}| {int(percent_used * 100)}%] {used_memory}/{total_memory}")    # Output the memory usage in raw numerical format (kB)
    
    else:  
        pids = pids_of_prog(args.program)  # Get the PIDs of the specified program
        if not pids:  # If no PIDs are found for the program
            print(f"{args.program} not found.")  # Output an error message
            
        else:
            total_program_memory = 0  # Initialize total memory usage for the program
            for pid in pids:
                rss_memory = rss_mem_of_pid(pid)  # Get RSS memory usage for each PID
                percent_used = rss_memory / total_memory  # Calculate percentage of total memory used by the process
                graph = percent_to_graph(percent_used, args.length)  # Generate a graphical representation of process memory

                if args.human_readable:  # If the human-readable flag is set
                    rss_memory_str = bytes_to_human_r(rss_memory)  # Convert RSS memory to human-readable format
                    total_memory_str = bytes_to_human_r(total_memory)  # Convert total memory to human-readable format

                    
                    print(f"{pid:<15} [{graph}| {int(percent_used * 100)}%] {rss_memory_str}/{total_memory_str}")  # Output the PID and memory usage with human-readable sizes
                else:
                    
                    print(f"{pid:<15} [{graph}| {int(percent_used * 100)}%] {rss_memory}/{total_memory}")   # Output the PID and memory usage in raw numerical format (kB)
                total_program_memory += rss_memory  
