import time
import psutil
import os
from prometheus_client import Gauge, start_http_server, Summary, Counter, Histogram

# Create metrics
summary = Summary('request_processing_seconds', 'Time spent processing request')
counter = Counter("launch_counter", "lauch_counter")
memory_gauge = Gauge('memory_usage', 'Current memory usage in bytes')
memory_histogram = Histogram('memory_usage_histogram', 'Memory usage distribution')


def get_current_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


@summary.time()
def process_request(t):
    """A dummy function that takes some time."""
    counter.inc()
    
    # Получаем и записываем использование памяти
    current_memory = get_current_memory()
    memory_gauge.set(current_memory)
    memory_histogram.observe(current_memory)
    
    print(f"request_processed | Memory: {current_memory / 1024 / 1024:.2f} MB")
    time.sleep(t)


if __name__ == '__main__':
    # Установите psutil если нет: pip install psutil
    start_http_server(8000)
    while True:
        process_request(1)
