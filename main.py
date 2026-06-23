import os
import filecmp
import difflib
from pathlib import Path


def compare_cet_files(file1, file2):
    with open(file1, 'r', encoding='utf-8', errors='replace') as f1, \
         open(file2, 'r', encoding='utf-8', errors='replace') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        
    diff = difflib.unified_diff(
        lines1, lines2, 
        fromfile=str(file1), 
        tofile=str(file2)
    )
    return list(diff)


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

    mismatched = {}
    for filename in files1:
        file_a = path1 / filename
        file_b = path2 / filename

        # check if files are identical
        if not filecmp.cmp(file_a, file_b, shallow=False):
            # If it's a .cet file, extract the exact content differences
            if filename.lower().endswith('.cet'):
                mismatched[filename] = compare_cet_files(file_a, file_b)
            else:
                mismatched[filename] = ["Binary or non-CET file contents differ.\n"]

    if not mismatched:
        return "Identical: All filenames and contents match perfectly."
    else:
        result = "Not Identical: The following files have different contents:\n"
        for filename, diff_lines in mismatched.items():
            result += f"\n{'='*40}\nDifferences in: {filename}\n{'='*40}\n"
            
            result += "".join(diff_lines)
                
        return result

# change these to whatever
folder_a = "./webapp"
folder_b = "./desktop"

result = compare_folders(folder_a, folder_b)
print(result)

output_path = "diff_output.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(result)
print(f"\nDiff written to {output_path}")