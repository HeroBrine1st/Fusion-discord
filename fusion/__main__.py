import sys
import os
from pkg_resources import resource_string

with open("test.txt", "w") as f:
    f.write("test")
print(sys.argv)

exit(0)
if len(sys.argv) < 2:
    print("Available commands:")
    print("\tstartproject")
    exit(0)

command = sys.argv

if command == "startproject":
    pass
else:
    print("Available commands:")
    print("\tstartproject")
