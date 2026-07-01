#!/usr/bin/env python3
import sys
import argparse
import os
import hashlib
import zlib
import pathlib

# Color codes
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RESET = '\033[0m'

# init-command Logic
def handle_init(args) : 
    try : 
        os.mkdir(".mgit")
        os.mkdir(".mgit/objects")
        os.mkdir(".mgit/ref")
        os.mkdir(".mgit/ref/heads")
        os.mkdir(".mgit/ref/tags")
        with open(".mgit/HEAD.txt", "w") as f: 
            f.write("ref: refs/ehads/main")
    except FileExistsError as e : 
        print("Already Initialized !")

# hash-object-Command Logic
def handle_hash_object(args) : 
    try : 
        file_path = pathlib.Path(getattr(args, "path", args))
        if file_path.exists() : 
            with open(file_path, "r") as f :
                raw_data = f.read()

                header_string = f"blob {len(raw_data.encode())}\0"
                blob_bytes = header_string.encode() + raw_data.encode()
                sha1_hash = hashlib.sha1(blob_bytes).hexdigest()
                compressed_blob_bytes = zlib.compress(blob_bytes)

                dir_path = pathlib.Path(f".mgit/objects/{sha1_hash[:2]}")
                if dir_path.exists() :
                    with open(f".mgit/objects/{sha1_hash[:2]}/{sha1_hash[2:]}", "wb") as f: 
                        f.write(compressed_blob_bytes)
                else : 
                    os.mkdir(dir_path)
                    with open(f".mgit/objects/{sha1_hash[:2]}/{sha1_hash[2:]}", "wb") as f: 
                        f.write(compressed_blob_bytes)
                
                print(sha1_hash)
                return sha1_hash
    except Exception as e : 
        print(e)  

# Cat-file-Command Logic
def handle_cat_file(args) : 
    try : 
        sha_hash = args.SHA
        dir_path = pathlib.Path(f".mgit/objects/{sha_hash[:2]}/{sha_hash[2:]}")

        if dir_path.exists() : 
            with open(dir_path, "rb") as f :
                blob_bytes = zlib.decompress(f.read())
                content_index = blob_bytes.find("\0".encode())
                print(blob_bytes[content_index+1: ])
    except Exception as e : 
        print(e)

# Add-Command Logic
def handle_add(args) :  
    entires = []      
    for file in args.files :  
        file_path = pathlib.Path(file) 
        
        # Check if the given file is directory 
        if file_path.is_dir() : 
            files_in_dir = os.listdir(file_path)
            if len(files_in_dir) == 0 : break

            for file in files_in_dir : 
                hash = handle_hash_object(f"{file_path}/{file}")
                entires.append(f"100644 {hash} 0 {file_path}/{file}\n".encode())
        else :
            try : 
                hash = handle_hash_object(file)
                entires.append(f"100644 {hash} 0 {file}\n".encode())
            except Exception as e : 
                print(e)

    with open(".mgit/index", "ab") as f : 
        f.writelines(entires)

# Status-Command Logic
def handle_status(args) : 
    files_in_working_dir = os.listdir()
    files_in_index = []
    index_file_path = pathlib.Path(".mgit/index") 

    # Check if the Index file is created
    # If not Created just mark all files in working dir as untracked
    if index_file_path.exists() : 
        with open(".mgit/index", "rb") as f: 
            entries = f.read().split("\n".encode())
            print("Changes to be commited :")
            for entry in entries: 
                if len(entry) > 2 : 
                    lst = entry.split(" ".encode())
                    file_name = lst[3].decode()
                    files_in_index.append(file_name)
                    print(f"\t {GREEN} {file_name}")

        print(f"{RESET}Untracked Files :")
        for file_name in files_in_working_dir :            
            if file_name not in files_in_index : 
                print(f"\t{RED} {file_name}")
    else : 
        print("Untracked Files :")
        for file_name in files_in_working_dir :            
                print(f"\t{RED} {file_name}")

# Commit-Command Logic
def handle_commit(args) : 
    with open(".mgit/index", "rb") as f : 
        index_data = f.read().decode().split("\n")
        for entry in index_data: 
            if len(entry) > 2 : 
                path = pathlib.Path(entry.split(" ")[3])
                if path.is_file() :     
                    print('file')
                elif path.is_dir() : 
                    print(dir)
                

# Create Main Parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="mode",required=True)

# Create init Parser
init_parser = subparsers.add_parser("init", help="Initialize a new respository.")
init_parser.set_defaults(func=handle_init)

# Create hash-object Parser
hash_object_parser = subparsers.add_parser("hash-object", help="Hash a object")
hash_object_parser.add_argument("path",type=str)
hash_object_parser.set_defaults(func=handle_hash_object)

# Create cat-file Parser
cat_file_parser = subparsers.add_parser("cat-file", help="View Content based on SHA.")
cat_file_parser.add_argument("SHA",type=str)
cat_file_parser.set_defaults(func=handle_cat_file)

# Create add Parser
add_parser = subparsers.add_parser("add", help="Added Files to Staging.")
add_parser.add_argument("files",nargs="+",type=str)
add_parser.set_defaults(func=handle_add)

# Create status Parser
status_parser = subparsers.add_parser("status", help="Few File Status.")
status_parser.set_defaults(func=handle_status)

# Create commit Parser
commit_parser = subparsers.add_parser("commit", help="Commit a file.")
commit_parser.add_argument("-m", type=str, help="Add Comment.")
commit_parser.set_defaults(func=handle_commit)

# Parse Args & Call Function
args = parser.parse_args()
args.func(args)

