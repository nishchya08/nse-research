# How to calculate execution time in Python

import time
start_time = time.perf_counter()

for i in range(100000000):
    pass  # Simulating a time-consuming task

end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.1f} seconds")