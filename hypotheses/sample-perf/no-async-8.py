import time

def add(x: int):
    return x + 1

def main():
    for _ in range(10_000):
        
        output = add(1)
        output = add(2)
        output = add(3)
        output = add(4)

        output = add(5)
        output = add(6)
        output = add(7)
        output = add(8)

    return output

start = time.perf_counter()
main()
end = time.perf_counter()
print(f"Time elapsed: {end - start:.8f}s.")