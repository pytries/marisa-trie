import concurrent.futures
import threading
import string

import pytest
import hypothesis.strategies as st


__all__ = ("text", "records", "run_threaded")


text = st.text(f"абвгдеёжзиклмнопрстуфхцчъыьэюя{string.ascii_lowercase}")
records = st.tuples(st.integers(min_value=0, max_value=2**16 - 1), st.booleans())


def run_threaded(
    func,
    max_workers=8,
    pass_count=False,
    pass_barrier=False,
    outer_iterations=1,
    prepare_args=None,
):
    """Runs a function many times in parallel.

    Copied from https://github.com/numpy/numpy/blob/main/numpy/testing/_private/utils.py
    Copyright (c) 2005-2025, NumPy Developers. All rights reserved.
    Full license: https://github.com/numpy/numpy/blob/main/LICENSE.txt
    """
    for _ in range(outer_iterations):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as tpe:
            if prepare_args is None:
                args = []
            else:
                args = prepare_args()
            if pass_barrier:
                barrier = threading.Barrier(max_workers)
                args.append(barrier)
            if pass_count:
                all_args = [(func, i, *args) for i in range(max_workers)]
            else:
                all_args = [(func, *args) for i in range(max_workers)]
            try:
                futures = []
                for arg in all_args:
                    futures.append(tpe.submit(*arg))
            except RuntimeError as e:
                pytest.skip(
                    f"Spawning {max_workers} threads failed with "
                    f"error {e!r} (likely due to resource limits on the "
                    "system running the tests)"
                )
            finally:
                if len(futures) < max_workers and pass_barrier:
                    barrier.abort()
            for f in futures:
                f.result()
