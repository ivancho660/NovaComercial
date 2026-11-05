
import concurrent.futures
import time
import urllib.request
import json
import statistics

URL = "http://127.0.0.1:5001/api/products"

def make_request(request_number):
    start = time.perf_counter()

    try:
        with urllib.request.urlopen(URL, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            elapsed = (time.perf_counter() - start) * 1000

            return {
                "request": request_number,
                "status": response.status,
                "thread": data.get("thread"),
                "products": data.get("total_products"),
                "time_ms": round(elapsed, 2)
            }

    except Exception as error:
        return {
            "request": request_number,
            "error": str(error)
        }


def run_test(number_of_requests):
    print(f"\nIniciando prueba con {number_of_requests} solicitudes simultáneas")

    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=number_of_requests
    ) as executor:

        results = list(
            executor.map(make_request, range(1, number_of_requests + 1))
        )

    total_time = (time.perf_counter() - start) * 1000

    successful = [
        result for result in results
        if result.get("status") == 200
    ]

    times = [result["time_ms"] for result in successful]
    threads = set(
        result["thread"] for result in successful
    )

    print("\nRESULTADOS")
    print("-" * 45)
    print("Solicitudes enviadas:", number_of_requests)
    print("Solicitudes exitosas:", len(successful))
    print("Solicitudes fallidas:", number_of_requests - len(successful))
    print("Hilos identificados:", len(threads))
    print("Tiempo total:", round(total_time, 2), "ms")

    if times:
        print("Tiempo promedio:", round(statistics.mean(times), 2), "ms")
        print("Tiempo máximo:", round(max(times), 2), "ms")
        print("Tiempo mínimo:", round(min(times), 2), "ms")

    print("\nDetalle de solicitudes:")
    for result in results:
        print(result)


if __name__ == "__main__":
    run_test(10)
    run_test(20)
    run_test(50)
