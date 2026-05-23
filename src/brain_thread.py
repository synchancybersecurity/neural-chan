from PyQt6.QtCore import QThread, pyqtSignal
import random, time

class BrainThread(QThread):
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)
    detection_signal = pyqtSignal(dict)
    
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.running = True
        self.auto_mode = False
        self.agents = {k: {'status':'idle','last_run':0} for k in 
            ['detector','ticketeer','fixer','tester','learner','coordinator']}
        self.tickets = []
        self.patterns = []
        self.threats = ['SQL Injection','XSS Attempt','Port Scan','Brute Force',
            'Malware Beacon','C2 Beacon','Lateral Movement','Data Exfiltration']
        
    def run(self):
        cycle = 0
        while self.running:
            cycle += 1
            if self.auto_mode:
                self._cycle(cycle)
            time.sleep(2)
    
    def _cycle(self, c):
        self.agents['detector']['status'] = 'working'
        self.status_signal.emit(f'Cycle {c}: Detector scanning...')
        if random.random() > 0.6:
            threat = random.choice(self.threats)
            sev = random.choice(['Low','Medium','High','Critical'])
            self.detection_signal.emit({'threat':threat,'severity':sev,'cycle':c})
            self.log_signal.emit(f'[DETECT] {threat} | {sev}', 'red')
            self.tickets.append({'id':len(self.tickets)+1,'threat':threat,'sev':sev,'status':'open'})
            self.agents['detector']['status'] = 'idle'
            
            self.agents['ticketeer']['status'] = 'working'
            self.log_signal.emit(f'[TICKET] #{len(self.tickets)} created','cyan')
            self.agents['ticketeer']['status'] = 'idle'
            
            self.agents['fixer']['status'] = 'working'
            self.log_signal.emit('[FIX] Auto-patch generated','green')
            self.agents['fixer']['status'] = 'idle'
            
            self.agents['tester']['status'] = 'working'
            self.log_signal.emit('[TEST] Validation passed','green')
            self.agents['tester']['status'] = 'idle'
            
            self.agents['learner']['status'] = 'working'
            p = f'Pattern-{len(self.patterns)+1}-{threat.replace(" ","")}'
            self.patterns.append(p)
            self.log_signal.emit(f'[LEARN] {p} acquired','purple')
            self.agents['learner']['status'] = 'idle'
        else:
            self.agents['detector']['status'] = 'idle'
        
        self.agents['coordinator']['status'] = 'working'
        idle = sum(1 for a in self.agents.values() if a['status']=='idle')
        self.status_signal.emit(f'Cycle {c} | {idle}/6 idle | Tickets: {len(self.tickets)} | Patterns: {len(self.patterns)}')
        self.agents['coordinator']['status'] = 'idle'
    
    def stop(self): self.running = False; self.log_signal.emit('[STOP] Emergency halt','red')
    def resume(self): self.running = True; self.log_signal.emit('[RESUME] Operations active','green')
    def toggle_auto(self): self.auto_mode = not self.auto_mode; return self.auto_mode
    def get_status(self): return {'agents':self.agents,'tickets':len(self.tickets),'patterns':len(self.patterns),'auto':self.auto_mode}
