import random
import string

def generate_password():
    symbols = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
    digits = ''.join(random.choice(string.digits) for _ in range(3))
    return f'{symbols}-{digits}'