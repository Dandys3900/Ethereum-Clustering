# Imports
from concurrent.futures import ThreadPoolExecutor

# Manages and divides functions into threads and waits for their completion
def startThreading(funcsList=[]):
    with ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        [executor.submit(func) for func in funcsList]
