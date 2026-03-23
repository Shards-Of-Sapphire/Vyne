import os
import time
import psutil
import argparse
from pathlib import Path
from multiprocessing import Process, Queue, cpu_count
from src.deepaudit.engine.parser import CodeParser
from src.deepaudit.scanners import ACTIVE_SCANNERS
from src.deepaudit.utils.logger import get_logger

# Initialize Sapphire Logger
logger = get_logger("BOMBARD")

class BombardmentEngine:
    def __init__(self, target_path, workers):
        self.target_path = Path(target_path)
        self.workers = workers if workers > 0 else cpu_count()
        self.results_queue = Queue()

    def get_payload(self):
        """Recursive walker for supported extensions."""
        extensions = {'.py', '.js', '.java'}
        payload = [
            str(p) for p in self.target_path.rglob('*') 
            if p.suffix in extensions and p.is_file()
        ]
        return payload

    @staticmethod
    def worker_task(files, queue):
        """
        Atomic Worker: Tests Lazy Instance Initialization.
        Each file gets a fresh Parser instance to test 'v0.2.0 Great Reset' logic.
        """
        process = psutil.Process(os.getpid())
        
        for file_path in files:
            start_time = time.perf_counter()
            try:
                # Eager at class, Lazy at instance (v0.2.0 Logic)
                parser = CodeParser(file_path) 
                ast = parser.parse()
                
                findings_count = 0
                if ast:
                    # Run the Explicit Manifest Registry
                    for scanner in ACTIVE_SCANNERS:
                        findings = scanner(ast)
                        findings_count += len(findings)

                duration = (time.perf_counter() - start_time) * 1000
                mem_usage = process.memory_info().rss / (1024 * 1024) # MB
                
                queue.put({
                    "status": "SUCCESS",
                    "file": file_path,
                    "ms": duration,
                    "mem_mb": mem_usage,
                    "findings": findings_count
                })
            except Exception as e:
                queue.put({"status": "ERROR", "file": file_path, "error": str(e)})

    def run(self):
        files = self.get_payload()
        total_files = len(files)
        logger.info(f"🚀 Bombardment Start: {total_files} files | {self.workers} workers")

        # Chunking payload for workers
        avg = len(files) // self.workers
        chunks = [files[i:i + avg] for i in range(0, len(files), avg)]

        processes = []
        for chunk in chunks:
            p = Process(target=self.worker_task, args=(chunk, self.results_queue))
            processes.append(p)
            p.start()

        # Telemetry Aggregation
        processed = 0
        errors = 0
        total_ms = 0
        peak_mem = 0

        while processed < total_files:
            res = self.results_queue.get()
            processed += 1
            if res["status"] == "SUCCESS":
                total_ms += res["ms"]
                peak_mem = max(peak_mem, res["mem_mb"])
            else:
                errors += 1
            
            if processed % 100 == 0:
                logger.info(f"Progress: {processed}/{total_files} | Errors: {errors}")

        for p in processes:
            p.join()

        self.report(total_files, errors, total_ms, peak_mem)

    def report(self, total, errors, total_ms, peak_mem):
        avg_speed = total_ms / (total - errors) if (total - errors) > 0 else 0
        logger.info("--- BOMBARDMENT REPORT ---")
        logger.info(f"Total Files: {total}")
        logger.info(f"Failed Parsings: {errors}")
        logger.info(f"Avg Latency: {avg_speed:.2f}ms/file")
        logger.info(f"Peak Worker RSS: {peak_mem:.2f}MB")
        logger.info("--------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeepAudit v0.2.0 Stress Tester")
    parser.add_argument("--path", required=True, help="Path to payload directory")
    parser.add_argument("--workers", type=int, default=0, help="Number of processes")
    args = parser.parse_args()

    bombard = BombardmentEngine(args.path, args.workers)
    bombard.run()
