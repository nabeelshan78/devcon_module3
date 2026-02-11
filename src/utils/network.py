import time
import requests
import statistics
from termcolor import colored

class NetworkSentinel:
    def __init__(self, target_url="https://1.1.1.1"):
        self.target = target_url

    def ping(self, runs=3):
        """
        Pings a high-availability server to estimate RTT (Round Trip Time).
        Returns: Average latency in milliseconds (ms).
        """
        latencies = []
        try:
            for _ in range(runs):
                start = time.time()
                requests.get(self.target, timeout=2)
                latencies.append((time.time() - start) * 1000)
            
            avg_latency = statistics.mean(latencies)
            return avg_latency
        except requests.RequestException:
            return 9999.0  # Max latency on failure

    def get_mode(self):
        """
        Decides the reasoning strategy based on current network health.
        """
        latency = self.ping()
        
        if latency < 300:
            status = colored(f"STRONG ({int(latency)}ms)", "green")
            mode = "DEEP_REASONING"
        elif latency < 1000:
            status = colored(f"MODERATE ({int(latency)}ms)", "yellow")
            mode = "STANDARD"
        else:
            status = colored(f"POOR ({int(latency)}ms)", "red")
            mode = "FAST_RESPONSE"
            
        print(f"[SYSTEM] Network Status: {status} -> Mode: {mode}")
        return mode