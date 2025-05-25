import csv
import sys
import time
from datetime import datetime
from types import FrameType
from typing import Optional

# ------------------------------------------------------------------------------
# High-precision total timer
# ------------------------------------------------------------------------------
gnStart: float = time.perf_counter()


# ------------------------------------------------------------------------------
# Cache the static stack trace once
# ------------------------------------------------------------------------------
def get_stack_trace() -> str:
    frame: Optional[FrameType] = sys._getframe()
    stack: list[str] = [frame.f_code.co_name]
    while frame is not None:
        name: str = frame.f_back.f_code.co_name
        if name == "<module>":
            break
        stack.insert(0, name)
        frame = frame.f_back
    return "/".join(reversed(stack[:-2]))


# ------------------------------------------------------------------------------
# log_event: prepare one row
# ------------------------------------------------------------------------------
def log_event(event: str, prev_time: float) -> tuple[list[str], float]:
    now_str: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current: float = time.perf_counter()
    elapsed: float = current - prev_time
    stack: str = get_stack_trace()
    return [event, f"{elapsed:.8f}", now_str, stack], current


# ------------------------------------------------------------------------------
# Main runner with batch writes
# ------------------------------------------------------------------------------
def run_logging_test(
    n: int = 100_000,
    output_path: str = f"writer_batches_{int(time.time())}.csv",
    batch_size: int = 10_000,
) -> tuple[list[str], float]:
    """
    - n:          total events to log
    - output_path: CSV file to write
    - batch_size: number of rows to buffer before flushing to disk
    """
    prev_time: float = gnStart
    last_row: list[str] = []
    buffer: list[list[str]] = []

    # Open once, write headers if needed
    if "{timestamp}" in output_path:
        output_path = output_path.format(timestamp=int(time.time()))
    with open(output_path, "w", newline="") as f:
        # with open(output_path, "a", newline="") as f:
        writer: csv.Writer = csv.writer(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        for i in range(1, n + 1):
            row, prev_time = log_event("Hello Daksh, this is an event!", prev_time)
            buffer.append(row)
            last_row = row

            # Flush every batch_size rows
            if i % batch_size == 0:
                writer.writerows(buffer)
                buffer.clear()

        # Flush any remainder
        if buffer:
            writer.writerows(buffer)

    total_time: float = time.perf_counter() - gnStart
    return last_row, total_time


# ------------------------------------------------------------------------------
# Run and report
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    final_row, duration = run_logging_test(
        n=100_000,
        batch_size=10_000,
    )
    quoted = ",".join(f'"{field}"' for field in final_row)
    print(quoted)
    print(f"Elapsed time: {duration:.2f} s")
