import os
import sys

def update_sys_path():
    root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # 2. Get the path directly to the lambdas folder
    lambdas_directory = os.path.join(root_directory, "lambdas")

    # 3. Add BOTH directories to sys.path
    sys.path.insert(0, root_directory)
    sys.path.insert(0, lambdas_directory)