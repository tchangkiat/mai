from concurrent.futures import ThreadPoolExecutor, wait
import sys
import time
import traceback

from mai.helpers import logging


class ThreadPoolExecutorStackTraced(ThreadPoolExecutor):
    def submit(self, fn, *args, **kwargs):
        """Submits the wrapped function instead of `fn`"""
        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs
        )

    def _function_wrapper(self, fn, *args, **kwargs):
        """Wraps `fn` in order to preserve the traceback of any kind of
        raised exception"""
        log = logging.Logging.get_instance()
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            log.error(sys.exc_info()[0](traceback.format_exc()))


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, function, parameters):
        """Add task to run later"""
        self.tasks.append({"function": function, "parameters": parameters})

    def run_tasks(self):
        """Run tasks that are added"""
        results = []
        with ThreadPoolExecutorStackTraced(max_workers=10) as executor:
            futures = []
            for task in self.tasks:
                if isinstance(task["parameters"], str):
                    futures = [executor.submit(task["function"], task["parameters"])]
                else:
                    futures = [
                        executor.submit(task["function"], parameter)
                        for parameter in task["parameters"]
                    ]

            bar = [
                " [=     ]",
                " [ =    ]",
                " [  =   ]",
                " [   =  ]",
                " [    = ]",
                " [     =]",
                " [    = ]",
                " [   =  ]",
                " [  =   ]",
                " [ =    ]",
            ]
            idx = 0
            while not self._all_futures_completed(futures):
                print(bar[idx % len(bar)], end="\r")
                time.sleep(0.2)
                idx += 1
            for future in futures:
                exception = future.exception()
                if not exception:
                    results.append(future.result())
        return results

    def _all_futures_completed(self, futures):
        for future in futures:
            if not future.done():
                return False
        return True
