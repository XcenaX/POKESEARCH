import string
import random

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def get_random_string_of_numbers(length):
    letters = ["0","1","2","3","4","5","6","7","8","9"]
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str