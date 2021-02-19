import random
import string

def pwd_gen(size):
	chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
	result = ''.join(random.SystemRandom().choice(chars) for x in range(size))
	return result