import concurrent
import concurrent.futures
import multiprocessing
import threading
import time

import requests

img_urls = [
    "https://cdn.pixabay.com/photo/2016/04/04/14/12/monitor-1307227_1280.jpg",
    "https://cdn.pixabay.com/photo/2018/07/14/11/33/earth-3537401_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/06/09/20/38/woman-1446557_1280.jpg",
]


def exercice_3(img_url: str):
    img_bytes = requests.get(img_url).content
    img_name = img_url.split("/")[4]
    with open(img_name, "wb") as img_file:
        img_file.write(img_bytes)
        print(f"{img_name} was downloaded")


if __name__ == "__main__":
    print("Multi processing")
    print("================")
    start = time.perf_counter()

    processes: list[multiprocessing.Process] = []

    for url in img_urls:
        process = multiprocessing.Process(target=exercice_3, args=[url])
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")

    print("Pool de threads")
    print("===============")
    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(exercice_3, img_urls)

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")

    print("Threading")
    print("=========")
    start = time.perf_counter()

    threads: list[threading.Thread] = []

    for url in img_urls:
        thread = threading.Thread(target=exercice_3, args=[url])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end = time.perf_counter()
    print(f"Tasks ended in {round(end - start, 2)} second(s)")
