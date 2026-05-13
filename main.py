import os
import filecmp
from pathlib import Path

def compare_folders(dir1, dir2):
    # Convert to Path objects for easier handling
    path1 = Path(dir1)
    path2 = Path(dir2)

    # 1. Check if both directories exist
    if not path1.is_dir() or not path2.is_dir():
        return "Error: One or both paths are not valid directories."

    # 2. Get all .bin files in both folders
    files1 = sorted([f.name for f in path1.glob("*.bin")])
    files2 = sorted([f.name for f in path2.glob("*.bin")])

    # 3. Compare filenames first
    if files1 != files2:
        return f"Not Identical: Filename lists do not match.\nFolder A: {files1}\nFolder B: {files2}"

    # 4. Compare file contents
    mismatched = []
    for filename in files1:
        file_a = path1 / filename
        file_b = path2 / filename

        # shallow=False ensures we compare the actual bits, not just metadata
        if not filecmp.cmp(file_a, file_b, shallow=False):
            mismatched.append(filename)

    # 5. Final Verdict
    if not mismatched:
        return "Identical: All .bin filenames and contents match perfectly."
    else:
        return f"Not Identical: The following files have different contents: {mismatched}"

# --- Example Usage ---
folder_a = "./webapp"
folder_b = "./desktop"

result = compare_folders(folder_a, folder_b)
print(result)