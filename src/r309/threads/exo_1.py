import multiprocessing
import threading
import time


def exercice_1(thread_num: int):
    for _ in range(5):
        print(f"Je suis la thread {thread_num}")
        time.sleep(1)


if __name__ == "__main__":
    print("Thread")
    print("======")
    start = time.perf_counter()

    thread_1 = threading.Thread(target=exercice_1, args=[1])
    thread_2 = threading.Thread(target=exercice_1, args=[2])

    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")

    print("Multi processing")
    print("================")
    start = time.perf_counter()

    process_1 = multiprocessing.Process(target=exercice_1, args=[1])
    process_2 = multiprocessing.Process(target=exercice_1, args=[2])
    process_1.start()
    process_2.start()
    process_1.join()
    process_2.join()

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")
