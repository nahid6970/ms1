import os, subprocess

os.chdir(r"C:\@delta\ms1\@Flask\5555_terminal\xxxx")
print("Starting PTY Terminal Server...")
subprocess.run(["node", "server.js"])
input("Press Enter to exit...")
