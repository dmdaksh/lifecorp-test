# LifeCorp Performance Refactor Take Home

## Hardware setup

I used a windows machine with WSL both having python 3.13 version installed

## Performance Analysis

The same 100 k-iteration Python logging loop completes in ~2-3 s on Linux but ~40-50s on Windows, and here are the detailed findings:

**Per-iteration file open/close overhead:**

- Opening and closing a file on each loop iteration is very cheap on ext4 but substantially slower on NTFS due to extra syscall and locking work

Sources:
<https://superuser.com/questions/256368/why-is-an-ext4-disk-check-so-much-faster-than-ntfs>
<https://stackoverflow.com/questions/4867468/should-i-keep-a-file-open-or-should-i-open-and-close-often>

**Delayed allocation vs. eager journaling**

- ext4’s delayed-allocation ("allocate-on-flush") batches writes and reduces fragmentation, greatly improving throughput
- NTFS, by contrast, journals each write eagerly and updates its Master File Table for every operation, adding significant I/O latency

Sources:
<https://superuser.com/questions/256368/why-is-an-ext4-disk-check-so-much-faster-than-ntfs>
<https://askubuntu.com/questions/689702/comparing-ntfs-and-ext4>  
<https://stackoverflow.com/questions/33226603/comparing-performance-of-ext4-and-ntfs>

**Real-time antivirus scanning**

- Windows Defender inspects every file creation and write unless explicitly excluded, often adding a 10x–20x slowdown to NTFS I/O paths

Sources:
<https://answers.microsoft.com/en-us/windows/forum/all/windows-defender-real-time-protection-service/fda3f73e-cc0a-4946-9b9d-3c05057ef90c>
<https://www.reddit.com/r/antivirus/comments/l3coav/windows_defender_performance_test>

**Superior Linux write-back caching**

- Linux aggressively batches small writes in its page cache before flushing, whereas NTFS’ caching is more coupled with metadata journaling and Defender’s scans, reducing its effectiveness

Sources:
<https://superuser.com/questions/369659/why-is-i-o-caching-performance-so-much-better-on-linux-than-windows>

**Unnecessary per-loop stack introspection**

- Calling sys._getframe() each iteration incurs frame-object creation and traversal costs. Python 3.11 only creates frames on demand, but repeated introspection remains non-trivial

Sources:
<https://stackoverflow.com/questions/45195921/why-is-inspect-currentframe-slower-than-sys-getframe>
<https://www.andy-pearce.com/blog/posts/2022/Dec/whats-new-in-python-311-performance-improvements>

### Recommended Improvements

- **Buffer in memory, batch writes:** Accumulate rows in a list and use a single writer.writerows() (or periodic batch flushes) to avoid per-call open/close overhead.
- **Cache the stack trace once:** If the call stack doesn’t change, compute it once outside the loop.
- **Use `time.perf_counter()`:** For low-overhead, high-resolution timing.
- **Exclude log directory from Defender:** Whitelist your log path to eliminate antivirus pauses.
- **Add a timestamp to the output filename:** Ensures each run writes to a new file, preventing accidental overwrites and making results traceable.

### With these changes, find below table showing speed comparisons

|                           | Windows  | Linux (WSL) |
|---------------------------|----------|-------------|
| Old Code (5 runs Average) | 41.31s   | 2.75s       |
| New Code (5 runs Average) | 0.85s    | 0.66s       |

## Additional Notes

Stepping back from the specifics, the refactor addresses several best practices. The original code had significant issues like poor structure, and inefficient patterns. The following changes were made to improve clarity, maintainability, and performance:

**Type Annotations & Self-Documentation**:
By adding precise type hints (event: str, -> tuple[list[str], float]) and docstrings, the code becomes self-documenting, IDEs can auto-complete and catch mismatches early, and on-boarding or code reviews get smoother.

**Single Responsibility & Clear Boundaries:**
Splitting the stack-trace logic, the logging logic, and the runner uses separate functions enforces the "one thing per function" principle. That makes each piece easier to test, reuse, and reason about in isolation.

**Explicit Entry Point & Reusability:**
Guarding execution behind if **name** == "**main**": turns the script into both a module and a CLI tool. You can now import run_logging_test in tests or other scripts without unintended side-effects.

**Consistent Naming & Style:**
Moving from cryptic globals (gnLastTime) to clear, PEP-8-compliant names (prev_time, run_logging_test) aligns with Python’s community conventions and immediately lowers the cognitive load on future readers.
