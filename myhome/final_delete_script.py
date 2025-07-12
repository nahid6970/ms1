import os
file_to_delete = "C:/ms1/myhome/delete_delete_script.py"
if os.path.exists(file_to_delete):
    os.remove(file_to_delete)
    print(f"Successfully deleted {file_to_delete}")
else:
    print(f"File not found: {file_to_delete}")
