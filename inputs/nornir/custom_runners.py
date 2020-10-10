#someone else wrote this , can't find the ref to credit

from concurrent.futures import ThreadPoolExecutor, as_completed
from nornir.core.task import AggregatedResult, Task
from nornir.core.inventory import Host
from typing import List
from tqdm import tqdm
from rich.progress import Progress, BarColumn


# custom runner using as_completed with rich progress bar
class runner_as_completed_rich:
    """
    ThreadedRunner runs the task over each host using threads
    Arguments:
        num_workers: number of threads to use
    """

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:
        """
        This is where the magic happens
        """
        # we instantiate the aggregated result
        result = AggregatedResult(task.name)

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.completed:>3.0f}/{task.total}",
        ) as progress:

            num_hosts = len(hosts)
            total = progress.add_task("[cyan]Completed...", total=num_hosts)
            successful = progress.add_task("[green]Successful...", total=num_hosts)
            changed = progress.add_task("[orange3]Changed...", total=num_hosts)
            error = progress.add_task("[red]Failed...", total=num_hosts)

            with ThreadPoolExecutor(max_workers=self.num_workers) as pool:
                futures = {pool.submit(task.copy().start, host): host for host in hosts}
                for future in as_completed(futures):
                    worker_result = future.result()
                    result[worker_result.host.name] = worker_result
                    progress.update(total, advance=1)
                    if worker_result.failed:
                        progress.update(error, advance=1)
                        progress.print(f"[red]{worker_result.host.name}: failure")
                    else:
                        progress.update(successful, advance=1)
                        progress.print(f"[green]{worker_result.host.name}: success")
                    if worker_result.changed:
                        progress.update(changed, advance=1)

        return result

    
# custom runner using as_completed with tqdm
class runner_as_completed_tqdm:
    """
    ThreadedRunner runs the task over each host using threads
    Arguments:
        num_workers: number of threads to use
    """

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:
        """
        This is where the magic happens
        """
        # we instantiate the aggregated result
        result = AggregatedResult(task.name)

        with tqdm(total=len(hosts), desc="progress",) as progress:
            with ThreadPoolExecutor(max_workers=self.num_workers) as pool:
                futures = {pool.submit(task.copy().start, host): host for host in hosts}
                for future in as_completed(futures):
                    worker_result = future.result()
                    result[worker_result.host.name] = worker_result
                    progress.update()
                    if worker_result.failed:
                        tqdm.write(f"{worker_result.host.name}: failure")
                    else:
                        tqdm.write(f"{worker_result.host.name}: success")

        return result

# custom runner using as_completed 
class runner_as_completed:
    """
    ThreadedRunner runs the task over each host using threads
    Arguments:
        num_workers: number of threads to use
    """

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:
        """
        This is where the magic happens
        """
        # we instantiate the aggregated result
        result = AggregatedResult(task.name)
        with ThreadPoolExecutor(max_workers=self.num_workers) as pool:
            futures = {pool.submit(task.copy().start, host): host for host in hosts}
            for future in as_completed(futures):
                worker_result = future.result() 
                result[worker_result.host.name] = worker_result
                if worker_result.failed:
                    print(f'{worker_result.host.name} - fail')
                else:
                    print(f'{worker_result.host.name} - success')

        return result




