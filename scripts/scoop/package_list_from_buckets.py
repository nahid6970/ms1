import os

# List of folders containing package lists
folders = [
    r"C:\Users\nahid\scoop\buckets\extras\bucket",
    r"C:\Users\nahid\scoop\buckets\main\bucket",
    r"C:\Users\nahid\scoop\buckets\nirsoft\bucket",
    r"C:\Users\nahid\scoop\buckets\nonportable\bucket",
    r"C:\Users\nahid\scoop\buckets\versions\bucket",
]

# Set the output text file
output_file = "D:\\@git\\ms1\\scripts\\scoop\\package_list_bucket.txt"

# Function to list packages from a folder
def list_packages(folder):
    packages = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".json"):
                package = file.split(".")[0]
                packages.append(package)
    return packages

# Get packages from all folders
all_packages = []
for folder in folders:
    all_packages.extend(list_packages(folder))

# Write packages to the output file
with open(output_file, "w") as file:
    file.write("\n".join(all_packages))

print("Package list has been saved to", output_file)
