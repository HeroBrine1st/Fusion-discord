import sys
import os
from pkg_resources import resource_string

# @HeroBrine1st, эта хрень работает и создает файл ровно там. откуда ее вызвали
# with open("test.txt", "w") as f:
#     f.write("test")

if len(sys.argv) < 3:
    print("Available commands:")
    print("\tstartproject <project name>")
    exit(0)

command = sys.argv[1]

if command == "startproject":
    project_name = sys.argv[2]
    manage_py: str = resource_string("fusion.management", "manage.py").decode("utf-8") \
        .replace("PASTEFUSIONSETTINGSHERE", "%s.settings" % project_name)
    os.mkdir(os.path.join(project_name, project_name))
    with open(os.path.join(project_name, "manage.py"), "w") as f:
        f.write(manage_py)
    settings_sample: str = resource_string("fusion.management", "settings_sample.py").decode("utf-8") \
        .replace()

else:
    print("Available commands:")
    print("\tstartproject")
