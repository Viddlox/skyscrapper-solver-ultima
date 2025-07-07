import time

def benchmark(func, *args, repeats=1):
    durations, res = [], 0
    for _ in range(repeats):
        start = time.perf_counter()
        res = func(*args)
        end = time.perf_counter()
        durations.append((end - start) * 1000)
    avg = sum(durations) / repeats
    print(f"\n{res}\nAverage execution time: {avg:.3f} ms")