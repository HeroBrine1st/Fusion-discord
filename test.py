import random
import string

print("".join(random.choice(string.printable) for i in range(64)))
