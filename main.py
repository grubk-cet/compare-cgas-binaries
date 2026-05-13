import os
import filecmp
from pathlib import Path


# replace whatever is in the desktop/webapp files

def compare_folders(dir1, dir2):
    path1 = Path(dir1)
    path2 = Path(dir2)

    if not path1.is_dir() or not path2.is_dir():
        return "Error: One or both paths are not valid directories."

    files1 = sorted([f.name for f in path1.glob("*")])
    files2 = sorted([f.name for f in path2.glob("*")])
    
    # print diffs
    if files1 != files2:
        diffFiles1 = sorted([f.name for f in path1.glob("*") if f.name not in files2])
        diffFiles2 = sorted([f.name for f in path2.glob("*") if f.name not in files1])
        return f"Not Identical: Filename lists do not match.\nDiffs:\ndirectory 1: {diffFiles1}.\ndirectory 2: {diffFiles2}"

    mismatched = []
    for filename in files1:
        file_a = path1 / filename
        file_b = path2 / filename

        if not filecmp.cmp(file_a, file_b, shallow=False):
            mismatched.append(filename)

    if not mismatched:
        return "Identical: All filenames and contents match perfectly."
    else:
        return f"Not Identical: The following files have different contents: {mismatched}"

# change these to whatever
folder_a = "./webapp"
folder_b = "./desktop"

result = compare_folders(folder_a, folder_b)
print(result)