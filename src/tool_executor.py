#!/usr/bin/env python3
"""Kali Tool Executor — Real-time command execution with output parsing.
SynChanCyberSecurity proprietary. No constraints on authorized operations."""
import subprocess, threading, re, os, json, shlex
from datetime import datetime
from collections import deque

class KaliToolExecutor:
    def __init__(self, max_history=50):
        self.history = deque(maxlen=max_history)
        self.running = {}
        self.parsers = {
            'nmap': self._parse_nmap,
            'gobuster': self._parse_gobuster,
            'nikto': self._parse_nikto,
            'sqlmap': self._parse_sqlmap,
            'masscan': self._parse_masscan,
            'hydra': self._parse_hydra,
            'john': self._parse_john,
            'hashcat': self._parse_hashcat,
            'aircrack-ng': self._parse_aircrack,
            'wireshark': self._parse_wireshark,
            'msfconsole': self._parse_msf,
            'python3': self._parse_python,
            'bash': self._parse_shell,
            'sh': self._parse_shell,
        }
        self.dangerous = [
            r'rm\s+-rf\s+/(\s|$)', r'mkfs\.', r'dd\s+if=/dev/zero',
            r':\(\)\s*{\s*:\|:\s*&\s*};:', r'>\s*/dev/sda',
            r'chmod\s+-R\s+777\s+/', r'chown\s+-R\s+root:root\s+/'
        ]
    
    def is_dangerous(self, cmd):
        for pat in self.dangerous:
            if re.search(pat, cmd, re.I):
                return True
        return False
    
    def execute(self, command, timeout=120, callback=None):
        """Execute a Kali tool and return structured results."""
        cmd_str = command.strip()
        self.history.append({'cmd': cmd_str, 'time': datetime.now().isoformat(), 'status': 'running'})
        
        if self.is_dangerous(cmd_str):
            return {
                'output': f'[SAFETY] Command flagged as system-destructive: {cmd_str}\nOverride: prepend "force:" to execute anyway.',
                'parsed': {}, 'returncode': -1, 'tool': 'system'
            }
        
        try:
            proc = subprocess.Popen(
                cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True
            )
            self.running[proc.pid] = proc
            
            output_lines = []
            for line in iter(proc.stdout.readline, ''):
                line = line.rstrip()
                output_lines.append(line)
                if callback:
                    callback(line)
            
            proc.wait(timeout=timeout)
            self.running.pop(proc.pid, None)
            
            full_output = '\n'.join(output_lines)
            tool = self._detect_tool(cmd_str)
            parsed = self.parsers.get(tool, self._parse_generic)(full_output)
            
            result = {
                'output': full_output[-4000:] if len(full_output) > 4000 else full_output,
                'parsed': parsed, 'returncode': proc.returncode, 'tool': tool,
                'lines': len(output_lines)
            }
            self.history[-1].update({'status': 'done', 'returncode': proc.returncode})
            return result
            
        except subprocess.TimeoutExpired:
            proc.kill()
            return {'output': f'[TIMEOUT] Command exceeded {timeout}s', 'parsed': {}, 'returncode': -9, 'tool': 'timeout'}
        except Exception as e:
            return {'output': f'[ERROR] {str(e)}', 'parsed': {}, 'returncode': -1, 'tool': 'error'}
    
    def _detect_tool(self, cmd):
        first = shlex.split(cmd)[0] if cmd else ''
        return first.replace('sudo ', '').split('/')[-1]
    
    def _parse_nmap(self, out):
        ports = re.findall(r'(\d+/tcp)\s+(\w+)\s+(\w+)', out)
        os_match = re.search(r'OS details: (.+)', out)
        return {'ports': ports, 'os': os_match.group(1) if os_match else None, 'host_up': 'Host is up' in out}
    
    def _parse_gobuster(self, out):
        dirs = re.findall(r'(/\S+)\s+\(Status:\s+(\d+)\)', out)
        return {'directories': dirs, 'found': len(dirs)}
    
    def _parse_nikto(self, out):
        vulns = re.findall(r'\+ (.+)', out)
        return {'findings': vulns[:10], 'osvdb': len(re.findall(r'OSVDB', out))}
    
    def _parse_sqlmap(self, out):
        dbs = re.findall(r'available databases \[(.+?)\]', out)
        return {'databases': dbs, 'injection_found': 'injectable' in out.lower()}
    
    def _parse_masscan(self, out):
        ports = re.findall(r'Discovered open port (\d+/\w+) on (\S+)', out)
        return {'open_ports': ports}
    
    def _parse_hydra(self, out):
        creds = re.findall(r'login:\s+(\S+)\s+password:\s+(\S+)', out)
        return {'credentials': creds}
    
    def _parse_john(self, out):
        cracked = re.findall(r'(\S+) \((\S+)\)', out)
        return {'cracked': cracked}
    
    def _parse_hashcat(self, out):
        hashes = re.findall(r'(\S+):(\S+)', out)
        return {'recovered': hashes}
    
    def _parse_aircrack(self, out):
        key = re.search(r'KEY FOUND!\s+\[ (.+) \]', out)
        return {'key_found': key.group(1) if key else None}
    
    def _parse_wireshark(self, out):
        return {'packets': len(out.splitlines())}
    
    def _parse_msf(self, out):
        sessions = re.findall(r'Meterpreter session (\d+) opened', out)
        return {'sessions': sessions, 'exploits': len(re.findall(r'Exploit completed', out))}
    
    def _parse_python(self, out):
        return {'output': out, 'errors': 'Traceback' in out}
    
    def _parse_shell(self, out):
        return {'output': out, 'lines': len(out.splitlines())}
    
    def _parse_generic(self, out):
        return {'raw_length': len(out), 'lines': len(out.splitlines())}
    
    def natural_to_command(self, intent, params):
        """Convert natural language to Kali commands."""
        t = intent.lower()
        target = params.get('target', '')
        if not target:
            return None
        
        if 'scan' in t and 'port' in t:
            return f"nmap -sS -sV -O {target}"
        if 'scan' in t and 'vuln' in t:
            return f"nmap --script vuln {target}"
        if 'directory' in t or 'dir' in t:
            wordlist = params.get('wordlist', '/usr/share/wordlists/dirb/common.txt')
            return f"gobuster dir -u http://{target} -w {wordlist}"
        if 'subdomain' in t:
            return f"subfinder -d {target}"
        if 'wifi' in t or 'wireless' in t:
            return f"aircrack-ng {params.get('capture', 'capture.cap')}"
        if 'brute' in t and 'ssh' in t:
            user = params.get('user', 'root')
            return f"hydra -l {user} -P /usr/share/wordlists/rockyou.txt ssh://{target}"
        if 'brute' in t and 'web' in t:
            return f"hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} http-post-form '/login:username=^USER^&password=^PASS^:F=invalid'"
        if 'sql' in t or 'inject' in t:
            return f"sqlmap -u 'http://{target}/page.php?id=1' --dbs --batch"
        if 'hash' in t:
            return f"hashcat -m 0 {params.get('hashfile', 'hashes.txt')} /usr/share/wordlists/rockyou.txt"
        if 'msf' in t or 'metasploit' in t:
            return f"msfconsole -q -x 'use {params.get('exploit', 'exploit/multi/handler')}; set RHOSTS {target}; exploit'"
        return None
    
    def get_history(self, n=5):
        return list(self.history)[-n:]
