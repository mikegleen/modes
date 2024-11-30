import re
import sys

major = sys.version_info.major
minor = sys.version_info.minor

m = re.match(r'(\d+)\.(\d+)', sys.argv[1])
reqmajor = int(m[1])
reqminor = int(m[2])

if (major, minor) < (reqmajor, reqminor):
    print(f'Python version too old.')
    sys.exit(-1)
