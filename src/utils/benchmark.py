import time

def benchmark(func, *args, repeats=5):
    durations, res = [], 0
    for _ in range(repeats):
        start = time.perf_counter()
        res = func(*args)
        end = time.perf_counter()
        durations.append((end - start) * 1000)
        print(f"\n== Result ==\n{res}")
    avg = sum(durations) / repeats
    print(f"\nAverage execution time: {avg:.3f} ms")