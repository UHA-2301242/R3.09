import multiprocessing
import threading
import time


def exercice_2(thread_num: int, counter: int):
    for count in range(counter, 0, -1):
        print(f"Thread {thread_num}: {count}")
        time.sleep(1)


if __name__ == "__main__":
    print("Thread")
    print("======")
    start = time.perf_counter()

    thread_1 = threading.Thread(target=exercice_2, args=[1, 5])
    thread_2 = threading.Thread(target=exercice_2, args=[2, 3])

    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")

    print("Multi processing")
    print("================")
    start = time.perf_counter()

    process_1 = multiprocessing.Process(target=exercice_2, args=[1, 5])
    process_2 = multiprocessing.Process(target=exercice_2, args=[2, 3])
    process_1.start()
    process_2.start()
    process_1.join()
    process_2.join()

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")
