import tracemalloc
import time
from contextlib import contextmanager
from typing import Literal, TypedDict
import linecache


type SnapshotIdentifier = int | str
type StatisticGroupBy = Literal["lineno", "filename", "traceback"]


class Units(TypedDict):
    B: int
    KB: int
    MB: int
    GB: int


class MemoryProfile(TypedDict):
    current: float
    peak: float
    current_bytes: int
    peak_bytes: int


class MemoryProfiler:
    """
    A comprehensive memory profiling utility using tracemalloc.
    """

    def __init__(
        self,
        top_n: int = 10,
        unit: str = "KB",
        include_tracemalloc: bool = False,
        filters: list[tracemalloc.Filter] | None = None,
    ):
        """
        Initialize the memory profiler.

        Args:
            top_n: Number of top allocations to display
            unit: Memory unit ('B', 'KB', 'MB', 'GB')
            include_tracemalloc: Include tracemalloc's own allocations
            filters: List of tracemalloc.Filter objects
        """
        self.top_n = top_n
        self.unit = unit.upper()
        self.include_tracemalloc = include_tracemalloc
        self.filters = filters or []
        self._started = False
        self._snapshots: list[tuple[str, tracemalloc.Snapshot, float]] = []
        self._timestamps: list[float] = []

        # Unit conversion factors
        self.unit_factors = Units(B=1, KB=1024, MB=1024**2, GB=1024**3)

    def _convert_bytes(self, bytes_value: float) -> float:
        """Convert bytes to the specified unit."""
        factor = self.unit_factors.get(self.unit, 1024)
        return bytes_value / factor

    def _format_size(self, bytes_value: float) -> str:
        """Format bytes with appropriate unit."""
        converted = self._convert_bytes(bytes_value)
        return f"{converted:.2f} {self.unit}"

    def start(self) -> None:
        """Start memory tracing."""
        if not self._started:
            tracemalloc.start()
            self._started = True
            print(f"Memory tracing started at {time.strftime('%H:%M:%S')}")

    def stop(self) -> None:
        """Stop memory tracing."""
        if self._started:
            tracemalloc.stop()
            self._started = False
            print(f"Memory tracing stopped at {time.strftime('%H:%M:%S')}")

    def take_snapshot(self, label: str = "") -> tracemalloc.Snapshot:
        """
        Take a memory snapshot with optional label.

        Args:
            label: Descriptive label for the snapshot

        Returns:
            tracemalloc.Snapshot object
        """
        if not self._started:
            self.start()

        snapshot = tracemalloc.take_snapshot()

        # Apply filters if not including tracemalloc
        if not self.include_tracemalloc:
            self.filters.append(tracemalloc.Filter(False, tracemalloc.__file__))

        if self.filters:
            snapshot = snapshot.filter_traces(self.filters)

        self._snapshots.append((label, snapshot, time.time()))
        self._timestamps.append(time.time())

        return snapshot

    def get_current_memory(self) -> MemoryProfile:
        """
        Get current memory usage statistics.

        Returns:
            Dictionary with current and peak memory usage
        """
        if not self._started:
            return MemoryProfile(
                current=0.0, peak=0.0, current_bytes=0, peak_bytes=0
            )

        current, peak = tracemalloc.get_traced_memory()
        return MemoryProfile(
            current=self._convert_bytes(current),
            peak=self._convert_bytes(peak),
            current_bytes=current,
            peak_bytes=peak,
        )

    def compare_snapshots(
        self,
        label1: SnapshotIdentifier = -2,
        label2: SnapshotIdentifier = -1,
        group_by: StatisticGroupBy = "lineno",
    ) -> list[tracemalloc.StatisticDiff]:
        """
        Compare two snapshots.

        Args:
            label1: Index or label of first snapshot
            label2: Index or label of second snapshot
            group_by: 'lineno', 'filename', or 'traceback'

        Returns:
            List of statistics showing differences
        """
        snapshot1 = self._get_snapshot(label1)
        snapshot2 = self._get_snapshot(label2)

        if snapshot1 is None or snapshot2 is None:
            return []

        return snapshot2.compare_to(snapshot1, group_by)

    def _get_snapshot(
        self, identifier: SnapshotIdentifier
    ) -> tracemalloc.Snapshot | None:
        """Get snapshot by index or label."""
        match identifier:
            case int() as idx if idx < 0:
                idx = len(self._snapshots) + idx
                return (
                    self._snapshots[idx][1]
                    if 0 <= idx < len(self._snapshots)
                    else None
                )
            case int() as idx if 0 <= idx < len(self._snapshots):
                return self._snapshots[idx][1]
            case str() as label:
                if found := next(
                    (snap for lbl, snap, _ in self._snapshots if lbl == label),
                    None,
                ):
                    return found
            case _:
                pass
        return None

    def display_stats(
        self, stats: list[tracemalloc.StatisticDiff], limit: int | None = None
    ) -> None:
        """
        Display memory statistics in a readable format.

        Args:
            stats: List of tracemalloc.Statistic objects
            limit: Maximum number of entries to display
        """
        display_limit = limit or self.top_n

        print(f"\n{'=' * 60}")
        print(f"Memory Statistics (Top {min(display_limit, len(stats))})")
        print(f"{'=' * 60}")

        for i, stat in enumerate(stats[:display_limit]):
            print(
                f"\n#{i + 1}: {self._format_size(stat.size)} "
                f"(count: {stat.count})"
            )

            # Print traceback using match for cleaner code
            match stat.traceback:
                case []:
                    print("  No traceback available")
                case frames:
                    for frame in frames[:3]:  # Limit traceback depth
                        line = linecache.getline(
                            frame.filename, frame.lineno
                        ).strip()
                        print(f"  {frame.filename}:{frame.lineno}: {line}")
                    if len(frames) > 3:
                        print(f"  ... and {len(frames) - 3} more frames")

    def display_comparison(
        self,
        label1: SnapshotIdentifier = -2,
        label2: SnapshotIdentifier = -1,
        limit: int | None = None,
    ) -> None:
        """Compare and display differences between two snapshots."""
        stats = self.compare_snapshots(label1, label2, "lineno")

        label1_str = self._get_label_str(label1)
        label2_str = self._get_label_str(label2)

        print(f"\n{'=' * 60}")
        print(f"Memory Comparison: {label1_str} → {label2_str}")
        print(f"{'=' * 60}")

        self.display_stats(stats, limit)

    def _get_label_str(self, identifier: SnapshotIdentifier) -> str:
        """Get string representation of snapshot label/index."""
        match identifier:
            case int() as idx if idx < 0:
                idx = len(self._snapshots) + idx
                if 0 <= idx < len(self._snapshots):
                    label = self._snapshots[idx][0]
                    return f"Snapshot {idx} ({label or 'unnamed'})"
            case int() as idx if 0 <= idx < len(self._snapshots):
                label = self._snapshots[idx][0]
                return f"Snapshot {idx} ({label or 'unnamed'})"
            case str() as label:
                return label
        return str(identifier)

    def profile_function(self, func, *args, **kwargs):
        """
        Profile a single function's memory usage.

        Args:
            func: Function to profile
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function's return value
        """
        self.start()

        # Take snapshot before
        self.take_snapshot(f"Before {func.__name__}")

        # Execute function
        result = func(*args, **kwargs)

        # Take snapshot after
        self.take_snapshot(f"After {func.__name__}")

        # Display comparison
        self.display_comparison(-2, -1)

        return result

    @contextmanager
    def profile_block(self, label: str = ""):
        """
        Context manager for profiling a code block.

        Usage:
            with profiler.profile_block("my_block"):
                # code to profile
        """
        self.start()
        self.take_snapshot(f"Start: {label}")

        try:
            yield
        finally:
            self.take_snapshot(f"End: {label}")
            self.display_comparison(-2, -1)

    def display_summary(self) -> None:
        """Display summary of all snapshots."""
        if not self._snapshots:
            print("No snapshots available.")
            return

        print(f"\n{'=' * 60}")
        print(f"Memory Profiling Summary ({len(self._snapshots)} snapshots)")
        print(f"{'=' * 60}")

        for i, (label, snapshot, timestamp) in enumerate(self._snapshots):
            stats = snapshot.statistics("lineno")
            total_size = sum(stat.size for stat in stats)
            total_count = sum(stat.count for stat in stats)

            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
            label_display = label or f"Snapshot {i}"

            print(f"\n{i}: {label_display} ({time_str})")
            print(
                f"  Total: {self._format_size(total_size)} "
                f"in {total_count} allocations"
            )

    def clear(self) -> None:
        """Clear all snapshots and reset."""
        self._snapshots.clear()
        self._timestamps.clear()
        if self._started:
            tracemalloc.clear_traces()
        print("Memory profiler cleared.")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        self.take_snapshot("Context Start")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.take_snapshot("Context End")
        self.display_comparison(-2, -1)
        self.stop()

    def get_snapshot_info(self, index: int = -1) -> dict[str, object]:
        """Get detailed information about a snapshot."""
        if not self._snapshots:
            return {}

        if index < 0:
            index = len(self._snapshots) + index

        label, snapshot, timestamp = self._snapshots[index]
        stats = snapshot.statistics("lineno")

        return {
            "index": index,
            "label": label,
            "timestamp": timestamp,
            "time_str": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(timestamp)
            ),
            "total_size": sum(stat.size for stat in stats),
            "total_count": sum(stat.count for stat in stats),
            "top_allocations": [
                {
                    "size": stat.size,
                    "count": stat.count,
                    "filename": stat.traceback[0].filename
                    if stat.traceback
                    else "",
                    "lineno": stat.traceback[0].lineno if stat.traceback else 0,
                }
                for stat in stats[:5]
            ],
        }

    def __init_subclass__(cls) -> None:
        pass


def test():
    profiler = MemoryProfiler(top_n=5)

    with profiler:
        data = [
            [i for i in range(100000)],  # List
            {i: str(i) for i in range(10000)},  # Dict
            {i for i in range(50000)},  # Set
            (i for i in range(20000)),  # Generator
        ]

        profiler.get_snapshot_info(-1)


if __name__ == "__main__":
    test()
