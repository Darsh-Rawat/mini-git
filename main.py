import argparse
import os
import hashlib
import zlib
import pathlib

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

def handle_hash_object(args) : 
    try : 
        raw_data = args.string
        header_string = f"blob {len(raw_data.encode())}\0"
        blob_bytes = header_string.encode() + raw_data.encode()
        sha1_hash = hashlib.sha1(blob_bytes).hexdigest()
        compressed_blob_bytes = zlib.compress(blob_bytes)
        print(sha1_hash)

        dir_path = pathlib.Path(f".mgit/objects/{sha1_hash[:2]}")
        if dir_path.exists() :
            with open(f".mgit/objects/{sha1_hash[:2]}/{sha1_hash[2:]}", "wb") as f: 
                f.write(compressed_blob_bytes)
        else : 
            os.mkdir(dir_path)
            with open(f".mgit/objects/{sha1_hash[:2]}/{sha1_hash[2:]}", "wb") as f: 
                f.write(compressed_blob_bytes)
    except Exception as e : 
        print(e)  

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

# Create Main Parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="mode",required=True)

# Create init Parser
init_parser = subparsers.add_parser("init", help="Initialize a new respository.")
init_parser.set_defaults(func=handle_init)

# Create hash-object Parser
hash_object_parser = subparsers.add_parser("hash-object", help="Hash a object")
hash_object_parser.add_argument("string",type=str)
hash_object_parser.set_defaults(func=handle_hash_object)

# Create cat-file Parser
cat_file_parser = subparsers.add_parser("cat-file", help="View Content based on SHA.")
cat_file_parser.add_argument("SHA",type=str)
cat_file_parser.set_defaults(func=handle_cat_file)

# Parse Args & Call Function
args = parser.parse_args()
args.func(args)

