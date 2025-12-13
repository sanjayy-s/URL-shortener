
import string

# Character set: 0-9, a-z, A-Z(base62)
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(ALPHABET)

def encode(num: int) -> str:
    #Converts a database ID (int) to a short code (str)
    if num == 0:
        return ALPHABET[0]
    arr = []
    while num:
        num, rem = divmod(num, BASE)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)

def decode(short_str: str) -> int:
    #Converts short code back to ID
    num = 0
    for char in short_str:
        num = num * BASE + ALPHABET.index(char)
    return num