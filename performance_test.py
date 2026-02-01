import time
import requests

def test():
    start = time.time()
    # Эмуляция запроса
    print(f"Benchmark: 1 image processed in {time.time()-start:.2f}s")

if __name__ == "__main__":
    test()