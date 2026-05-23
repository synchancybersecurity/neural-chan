"""System Monitor — feeds live CPU/memory/process data into Neural Chan's learning engine."""
import os, json, time, threading
from datetime import datetime
from collections import deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class SystemMonitor:
    def __init__(self, data_dir='~/neural-chan/data', history_size=300):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.metrics_file = os.path.join(self.data_dir, 'system_metrics.json')
        self.history = deque(maxlen=history_size)
        self.running = False
        self.thread = None
        self.interval = 2.0
        self._load_history()
        
    def _load_history(self):
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                self.history.extend(data[-self.history.maxlen:])
        except:
            pass
    
    def _save(self):
        with open(self.metrics_file, 'w') as f:
            json.dump(list(self.history), f, indent=2)
    
    def _collect(self):
        if not PSUTIL_AVAILABLE:
            return self._fallback_collect()
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            procs = len(psutil.pids())
            load = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            top_procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if p.info['cpu_percent'] and p.info['cpu_percent'] > 1.0:
                        top_procs.append({
                            'pid': p.info['pid'],
                            'name': p.info['name'],
                            'cpu': round(p.info['cpu_percent'], 1)
                        })
                except:
                    pass
            top_procs = sorted(top_procs, key=lambda x: x['cpu'], reverse=True)[:5]
            
            return {
                'time': datetime.now().isoformat(),
                'cpu_percent': round(cpu, 1),
                'mem_percent': round(mem.percent, 1),
                'mem_used_gb': round(mem.used / (1024**3), 2),
                'mem_total_gb': round(mem.total / (1024**3), 2),
                'disk_percent': round(disk.percent, 1),
                'net_sent_mb': round(net.bytes_sent / (1024**2), 2),
                'net_recv_mb': round(net.bytes_recv / (1024**2), 2),
                'processes': procs,
                'load_1m': round(load[0], 2),
                'load_5m': round(load[1], 2),
                'load_15m': round(load[2], 2),
                'top_processes': top_procs
            }
        except Exception as e:
            return {'time': datetime.now().isoformat(), 'error': str(e)}
    
    def _fallback_collect(self):
        try:
            with open('/proc/loadavg', 'r') as f:
                load = f.read().split()[:3]
            return {
                'time': datetime.now().isoformat(),
                'load_1m': float(load[0]),
                'load_5m': float(load[1]),
                'load_15m': float(load[2]),
                'cpu_percent': 0.0,
                'mem_percent': 0.0,
                'note': 'psutil not installed. Run: sudo apt-get install python3-psutil'
            }
        except:
            return {'time': datetime.now().isoformat(), 'error': 'No system metrics available'}
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _loop(self):
        while self.running:
            metric = self._collect()
            self.history.append(metric)
            if len(self.history) % 10 == 0:
                self._save()
            time.sleep(self.interval)
    
    def get_latest(self):
        return self.history[-1] if self.history else None
    
    def get_summary(self):
        if not self.history:
            return "No metrics collected yet."
        latest = self.history[-1]
        cpu = latest.get('cpu_percent', 0)
        mem = latest.get('mem_percent', 0)
        procs = latest.get('processes', 0)
        load = latest.get('load_1m', 0)
        return f"CPU: {cpu}% | MEM: {mem}% | PROCS: {procs} | LOAD: {load}"
    
    def get_anomalies(self):
        if len(self.history) < 10:
            return []
        anomalies = []
        recent = list(self.history)[-10:]
        avg_cpu = sum(m.get('cpu_percent', 0) for m in recent) / len(recent)
        avg_mem = sum(m.get('mem_percent', 0) for m in recent) / len(recent)
        
        latest = recent[-1]
        if latest.get('cpu_percent', 0) > avg_cpu * 2 and latest.get('cpu_percent', 0) > 50:
            anomalies.append(f"CPU spike: {latest['cpu_percent']}% (avg: {round(avg_cpu,1)}%)")
        if latest.get('mem_percent', 0) > 90:
            anomalies.append(f"Memory critical: {latest['mem_percent']}%")
        if latest.get('load_1m', 0) > 4.0:
            anomalies.append(f"System load high: {latest['load_1m']}")
        
        return anomalies
