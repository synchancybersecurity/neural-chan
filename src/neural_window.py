import sys, subprocess, random, math
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton, QLabel,
    QStatusBar, QDockWidget, QSlider, QComboBox, QLineEdit, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction, QKeySequence, QLinearGradient, QPainter
from neural_canvas import NeuralCanvas
from neural_conversation_v2 import NeuralConversationV2
from memory_exporter import MemoryExporter
from system_monitor import SystemMonitor
from web_learner import WebLearner
from neural_conversation_v2 import NeuralConversationV2
from memory_exporter import MemoryExporter
from system_monitor import SystemMonitor
from web_learner import WebLearner
from neural_conversation import NeuralConversation
from kaomoji_widget import KaomojiWidget

class NeuralWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Neural Chan OS v2.0 — SELF-LEARNING')
        self.setMinimumSize(1200, 700)
        self.resize(1400, 850)
        self.setStyleSheet("""
            QMainWindow { background: #050508; }
            QWidget { background: #050508; color: #ff0033; font-family: 'Courier New'; }
            QTreeWidget { background: #0a0a10; color: #ff5555; border: 1px solid #330000; border-radius: 4px; }
            QTreeWidget::item { padding: 3px; }
            QTreeWidget::item:selected { background: #330000; color: #ffffff; border-radius: 2px; }
            QTreeWidget::item:hover { background: #1a0000; }
            QTextEdit { background: #020205; color: #00ff55; border: 1px solid #003300; font-family: 'Courier New'; font-size: 10px; border-radius: 4px; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a1a, stop:1 #0a0a0a); color: #ff0033; border: 1px solid #ff0033; border-radius: 4px; padding: 4px; font-weight: bold; font-size: 10px; }
            QPushButton:hover { background: #330000; border-color: #ff3366; }
            QPushButton:pressed { background: #ff0033; color: #000000; }
            QSlider::groove:horizontal { background: #330000; height: 4px; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ff0033; width: 12px; height: 12px; border-radius: 6px; }
            QComboBox { background: #0a0a10; color: #ff0033; border: 1px solid #ff0033; border-radius: 4px; padding: 3px; font-size: 10px; }
            QLineEdit { background: #0a0a10; color: #ff5555; border: 1px solid #330000; border-radius: 4px; padding: 4px; font-size: 10px; }
            QCheckBox { color: #ff5555; spacing: 4px; font-size: 10px; }
            QGroupBox { color: #ff0033; border: 1px solid #330000; border-radius: 6px; margin-top: 8px; padding-top: 8px; font-weight: bold; font-size: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            QTabWidget::pane { background: #050508; border: 1px solid #330000; border-radius: 4px; }
            QTabBar::tab { background: #0a0a10; color: #ff5555; padding: 6px 10px; font-size: 10px; border: 1px solid #330000; border-bottom: none; border-radius: 4px 4px 0 0; }
            QTabBar::tab:selected { background: #330000; color: #ffffff; border-color: #ff0033; }
            QLabel { color: #ff5555; font-size: 10px; }
            QStatusBar { background: #0a0a10; color: #ff0033; border-top: 1px solid #330000; font-size: 10px; }
            QFrame { border: 1px solid #330000; border-radius: 4px; }
            QDockWidget { color: #ff0033; }
            QDockWidget::title { background: #0a0a10; padding: 6px; font-size: 10px; }
        """)
        self.brain = None
        self.system_monitor = SystemMonitor()
        self.web_learner = WebLearner()
        self.memory_exporter = MemoryExporter()
        self.conversation = NeuralConversationV2(
            system_monitor=self.system_monitor,
            web_learner=self.web_learner
        )
        self.conversation = NeuralConversation()
        self._setup_menubar()
        self._setup_central()
        self._setup_dock_left()
        self._setup_dock_right()
        self._setup_statusbar()
        self._setup_global_timer()
        self._setup_system_monitor()
        self._setup_auto_save()
    
    def _setup_menubar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet('background: #0a0a10; color: #ff0033; border-bottom: 1px solid #330000; font-size: 11px;')
        file_menu = menubar.addMenu('FILE')
        for label, shortcut, cb in [
            ('New Session', 'Ctrl+N', self._new_session),
            ('Export Logs', 'Ctrl+E', self._export_logs),
            ('Exit', 'Ctrl+Q', self.close)
        ]:
            act = QAction(f'{label} ({shortcut})', self)
            act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(cb)
            file_menu.addAction(act)
        neural_menu = menubar.addMenu('NEURAL')
        for label, shortcut, cb in [
            ('Detect Now', 'Ctrl+D', self._detect_now),
            ('Toggle Auto', 'Ctrl+A', self._toggle_auto),
            ('Emergency Stop', 'Ctrl+Shift+K', self._emergency_stop)
        ]:
            act = QAction(f'{label} ({shortcut})', self)
            if shortcut: act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(cb)
            neural_menu.addAction(act)
        neural_menu.addSeparator()
        resume_act = QAction('Resume', self)
        resume_act.triggered.connect(self._resume)
        neural_menu.addAction(resume_act)
        tools_menu = menubar.addMenu('TOOLS')
        categories = {
            'Recon': ['Nmap','Masscan','Shodan CLI','DNS Enum','WHOIS','theHarvester','OSINT'],
            'Web App': ['SQLMap','Nikto','Dirb','Gobuster','Burp Suite','OWASP ZAP','WFuzz'],
            'Wireless': ['Aircrack-ng','Wifite','Reaver','Fern WiFi','Kismet','Bully','PixieWPS'],
            'Exploitation': ['Metasploit','BeEF','SearchSploit','ExploitDB','Armitage','Commix'],
            'Passwords': ['John','Hashcat','Hydra','Medusa','Crunch','CeWL','Patator'],
            'Forensics': ['Autopsy','Sleuth Kit','Volatility','Binwalk','ExifTool','Bulk Extractor'],
            'Social Eng': ['SEToolkit','Evilginx2','Gophish','King Phisher','SocialFish'],
            'Defense': ['Snort','Suricata','OSSEC','Wazuh','Bro/Zeek']
        }
        for cat, tools in categories.items():
            cat_menu = tools_menu.addMenu(cat)
            for tool in tools:
                act = QAction(tool, self)
                act.triggered.connect(lambda checked, t=tool: self._launch_tool(t))
                cat_menu.addAction(act)
        settings_menu = menubar.addMenu('SETTINGS')
        prefs_act = QAction('Preferences', self)
        prefs_act.triggered.connect(self._show_settings)
        settings_menu.addAction(prefs_act)
        reset_act = QAction('Reset to Defaults', self)
        reset_act.triggered.connect(self._reset_defaults)
        settings_menu.addAction(reset_act)
        help_menu = menubar.addMenu('HELP')
        docs_act = QAction('Documentation', self)
        docs_act.triggered.connect(lambda: self._cli_log('Neural Chan OS v1.5.1 | DEBUGGED | 6 agents | 14 categories | Kali Native','cyan'))
        help_menu.addAction(docs_act)
        about_act = QAction('About', self)
        about_act.triggered.connect(lambda: QMessageBox.about(self, 'About', 'Neural Chan OS v1.5.1\nSynChanCyberSecurity 2026\nDebugged Layout Edition\nKali Linux Native Desktop App'))
        help_menu.addAction(about_act)
    
    def _setup_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # TOP: Kaomoji + Neural Canvas (50/50 split)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.setHandleWidth(2)
        top_splitter.setStyleSheet('QSplitter::handle { background: #330000; }')
        
        kaomoji_container = QFrame()
        kaomoji_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 8px; background: #08080c; }')
        kaomoji_layout = QVBoxLayout(kaomoji_container)
        kaomoji_layout.setContentsMargins(4, 4, 4, 4)
        kaomoji_layout.setSpacing(2)
        self.kaomoji = KaomojiWidget()
        self.kaomoji.setMinimumWidth(280)
        self.kaomoji.setMinimumHeight(200)
        self.kaomoji.speak_signal.connect(self._on_speak)
        kaomoji_layout.addWidget(self.kaomoji, 1)
        top_splitter.addWidget(kaomoji_container)
        
        canvas_container = QFrame()
        canvas_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 6px; background: #08080c; }')
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(2, 2, 2, 2)
        self.canvas = NeuralCanvas()
        self.canvas.setMinimumWidth(350)
        self.canvas.setMinimumHeight(250)
        canvas_layout.addWidget(self.canvas)
        top_splitter.addWidget(canvas_container)
        top_splitter.setSizes([320, 780])
        main_layout.addWidget(top_splitter, 4)
        
        # MIDDLE: CLI Terminal (compact)
        cli_frame = QFrame()
        cli_frame.setStyleSheet('QFrame { border: 1px solid #003300; border-radius: 6px; background: #020205; }')
        cli_layout = QVBoxLayout(cli_frame)
        cli_layout.setContentsMargins(4, 4, 4, 4)
        cli_layout.setSpacing(2)
        
        cli_header = QHBoxLayout()
        cli_header.setSpacing(8)
        cli_title = QLabel('CLI')
        cli_title.setFont(QFont('Courier', 9, QFont.Weight.Bold))
        cli_title.setStyleSheet('color: #00ff55;')
        cli_header.addWidget(cli_title)
        cli_hint = QLabel('detect | status | agents | tickets | memory | patterns | stop | resume | clear | speak | theme | help')
        cli_hint.setFont(QFont('Courier', 7))
        cli_hint.setStyleSheet('color: #005500;')
        cli_header.addWidget(cli_hint)
        cli_layout.addLayout(cli_header)
        
        self.cli_output = QTextEdit()
        self.cli_output.setReadOnly(True)
        self.cli_output.setMinimumHeight(80)
        self.cli_output.setMaximumHeight(120)
        self.cli_output.setStyleSheet('QTextEdit { background: #020205; color: #00ff55; border: none; font-family: Courier New; font-size: 10px; }')
        cli_layout.addWidget(self.cli_output)
        
        cli_input_layout = QHBoxLayout()
        cli_input_layout.setSpacing(4)
        prompt_label = QLabel('>')
        prompt_label.setFont(QFont('Courier', 10, QFont.Weight.Bold))
        prompt_label.setStyleSheet('color: #ff0033;')
        cli_input_layout.addWidget(prompt_label)
        self.cli_input = QLineEdit()
        self.cli_input.setPlaceholderText('Enter command...')
        self.cli_input.returnPressed.connect(self._cli_execute)
        self.cli_input.setStyleSheet('QLineEdit { background: #0a0a10; color: #00ff55; border: 1px solid #003300; border-radius: 4px; padding: 4px; font-family: Courier New; font-size: 10px; } QLineEdit:focus { border-color: #00ff55; }')
        cli_input_layout.addWidget(self.cli_input, 1)
        run_btn = QPushButton('RUN')
        run_btn.setFont(QFont('Courier', 8, QFont.Weight.Bold))
        run_btn.clicked.connect(self._cli_execute)
        cli_input_layout.addWidget(run_btn)
        clear_btn = QPushButton('CLR')
        clear_btn.setFont(QFont('Courier', 8, QFont.Weight.Bold))
        clear_btn.clicked.connect(self.cli_output.clear)
        cli_input_layout.addWidget(clear_btn)
        cli_layout.addLayout(cli_input_layout)
        main_layout.addWidget(cli_frame, 1)
        
        # BOTTOM: Compact Dock Bar
        dock_container = QFrame()
        dock_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 6px; background: #08080c; }')
        dock_layout = QHBoxLayout(dock_container)
        dock_layout.setContentsMargins(4, 4, 4, 4)
        dock_layout.setSpacing(4)
        
        dock_buttons = [
            ('SET', self._show_settings, '#ff0033'),
            ('ARS', self._toggle_arsenal, '#ff3366'),
            ('SCN', self._detect_now, '#00ff55'),
            ('TKT', self._show_tickets, '#00ffff'),
            ('MEM', self._show_memory, '#ff00ff'),
            ('AUT', self._toggle_auto, '#ffff00'),
            ('STP', self._emergency_stop, '#ff0000')
        ]
        for text, cb, color in dock_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(28)
            btn.setMaximumHeight(28)
            btn.setFont(QFont('Courier', 8, QFont.Weight.Bold))
            btn.setStyleSheet(f'QPushButton {{ background: #0a0a10; color: {color}; border: 1px solid {color}; border-radius: 4px; padding: 2px 6px; font-size: 9px; }} QPushButton:hover {{ background: #330000; }} QPushButton:pressed {{ background: {color}; color: #000000; }}')
            btn.clicked.connect(cb)
            dock_layout.addWidget(btn)
        main_layout.addWidget(dock_container)
    
    def _setup_dock_left(self):
        self.arsenal_dock = QDockWidget('ARSENAL', self)
        self.arsenal_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.arsenal_dock.setStyleSheet('QDockWidget::title { background: #0a0a10; padding: 6px; font-size: 10px; }')
        arsenal_widget = QWidget()
        arsenal_layout = QVBoxLayout(arsenal_widget)
        arsenal_layout.setContentsMargins(4, 4, 4, 4)
        self.arsenal_tree = QTreeWidget()
        self.arsenal_tree.setHeaderLabel('Double-click to launch')
        self.arsenal_tree.setMinimumWidth(220)
        self.arsenal_tree.setStyleSheet('QTreeWidget { background: #0a0a10; border: 1px solid #330000; border-radius: 4px; font-size: 10px; } QTreeWidget::item { padding: 3px; } QTreeWidget::item:selected { background: #330000; }')
        tools_data = {
            'Recon': ['Nmap','Masscan','Shodan','DNS Enum','WHOIS','OSINT','theHarvester'],
            'Tickets': ['Queue','Deduplication','Auto-Router','SLA','Escalation'],
            'Fix': ['Patch Gen','Diff Creator','Rollback','Templates','Hotfix'],
            'Test': ['Unit Tests','Integration','Regression','Performance','Fuzzing'],
            'Learn': ['Pattern Recognition','Confidence','Prevention','Archive','Clustering'],
            'Coord': ['Health Monitor','Conflict Resolver','File Locks','Load Balancer'],
            'Safety': ['Retry Limiter','Stuck-State','Loop Detector','E-Stop','Audit'],
            'Network': ['Packet Sniffer','Proxy Chains','Tor','VPN','MAC Spoofer'],
            'Exploit': ['Metasploit','BeEF','SEToolkit','SearchSploit','ExploitDB'],
            'Passwords': ['John','Hashcat','Hydra','Medusa','Crunch'],
            'Wireless': ['Aircrack-ng','Wifite','Reaver','Fern','Kismet'],
            'Web App': ['SQLMap','Nikto','Dirb','Gobuster','Burp Suite'],
            'Forensics': ['Autopsy','Sleuth Kit','Volatility','Binwalk','ExifTool'],
            'Social Eng': ['SEToolkit','Evilginx2','Gophish','King Phisher','SocialFish']
        }
        for category, tools in tools_data.items():
            cat_item = QTreeWidgetItem(self.arsenal_tree)
            cat_item.setText(0, f'[ {category} ]')
            cat_item.setFont(0, QFont('Courier', 9, QFont.Weight.Bold))
            cat_item.setExpanded(True)
            for tool in tools:
                tool_item = QTreeWidgetItem(cat_item)
                tool_item.setText(0, f'  >> {tool}')
                tool_item.setFont(0, QFont('Courier', 8))
        self.arsenal_tree.itemDoubleClicked.connect(self._on_tool_doubleclick)
        arsenal_layout.addWidget(self.arsenal_tree)
        self.arsenal_dock.setWidget(arsenal_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.arsenal_dock)

    def _setup_dock_right(self):
        self.settings_dock = QDockWidget('SETTINGS', self)
        self.settings_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.settings_dock.setStyleSheet('QDockWidget::title { background: #0a0a10; padding: 6px; font-size: 10px; }')
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(4, 4, 4, 4)
        tabs = QTabWidget()
        tabs.setStyleSheet('QTabBar::tab { font-size: 9px; padding: 4px 8px; }')
        
        ai_tab = QWidget()
        ai_layout = QFormLayout(ai_tab)
        ai_layout.setSpacing(4)
        ai_layout.addRow('Pitch:', self._slider(0.5, 3.0, 1.5, 10))
        ai_layout.addRow('Speed:', self._slider(0.5, 3.0, 1.2, 10))
        ai_layout.addRow('Volume:', self._slider(0, 100, 80, 1))
        ai_layout.addRow('Auto-Greet:', QCheckBox())
        personality = QComboBox()
        personality.addItems(['Analytical','Aggressive','Friendly','Silent'])
        ai_layout.addRow('Personality:', personality)
        tabs.addTab(ai_tab, 'AI')
        
        net_tab = QWidget()
        net_layout = QFormLayout(net_tab)
        net_layout.setSpacing(4)
        net_layout.addRow('Proxy:', QLineEdit('socks5://127.0.0.1:9050'))
        net_layout.addRow('VPN:', QCheckBox())
        net_layout.addRow('DNS:', QLineEdit('1.1.1.1'))
        net_layout.addRow('MAC Spoof:', QCheckBox())
        net_layout.addRow('Tor:', QCheckBox())
        tabs.addTab(net_tab, 'Net')
        
        sec_tab = QWidget()
        sec_layout = QFormLayout(sec_tab)
        sec_layout.setSpacing(4)
        sec_layout.addRow('Kill Switch:', QLineEdit('Ctrl+Shift+K'))
        sec_layout.addRow('Timeout:', self._slider(1, 60, 30, 1))
        sec_layout.addRow('Mem Wipe:', QCheckBox())
        sec_layout.addRow('Demo:', QCheckBox())
        sec_layout.addRow('PIN:', QLineEdit('1337'))
        tabs.addTab(sec_tab, 'Sec')
        
        scan_tab = QWidget()
        scan_layout = QFormLayout(scan_tab)
        scan_layout.setSpacing(4)
        scan_layout.addRow('Target:', QLineEdit('192.168.1.0/24'))
        scan_layout.addRow('Threads:', self._slider(1, 100, 50, 1))
        scan_layout.addRow('Ports:', QLineEdit('1-65535'))
        scan_layout.addRow('Timeout:', self._slider(1, 30, 5, 1))
        scan_layout.addRow('Aggro:', QCheckBox())
        tabs.addTab(scan_tab, 'Scan')
        
        disp_tab = QWidget()
        disp_layout = QFormLayout(disp_tab)
        disp_layout.setSpacing(4)
        theme = QComboBox()
        theme.addItems(['Crimson','Blue','Green','Amber','Void'])
        disp_layout.addRow('Theme:', theme)
        disp_layout.addRow('Bright:', self._slider(10, 100, 80, 1))
        disp_layout.addRow('Anim:', QCheckBox(checked=True))
        disp_layout.addRow('Font:', self._slider(8, 16, 11, 1))
        disp_layout.addRow('Compact:', QCheckBox())
        tabs.addTab(disp_tab, 'Disp')
        
        sys_tab = QWidget()
        sys_layout = QFormLayout(sys_tab)
        sys_layout.setSpacing(4)
        sys_layout.addRow('Autostart:', QCheckBox())
        sys_layout.addRow('Backup:', QPushButton('Backup'))
        sys_layout.addRow('Export:', QPushButton('Export'))
        reset_btn = QPushButton('RESET')
        reset_btn.setStyleSheet('background: #330000; color: #ff0000; font-weight: bold; font-size: 10px;')
        sys_layout.addRow('Danger:', reset_btn)
        tabs.addTab(sys_tab, 'Sys')
        
        settings_layout.addWidget(tabs)
        self.settings_dock.setWidget(settings_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)
    
    def _slider(self, min_v, max_v, default, scale):
        s = QSlider(Qt.Orientation.Horizontal)
        s.setRange(int(min_v * scale), int(max_v * scale))
        s.setValue(int(default * scale))
        return s
    
    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('Neural Chan OS v2.0 | Ready | Agents: 6/6 Idle | CPU: -- | MEM: --')
        self._update_statusbar()
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_statusbar)
        self.status_timer.start(3000)
    
    def _update_statusbar(self):
        try:
            if self.system_monitor and self.system_monitor.history:
                latest = self.system_monitor.get_latest()
                cpu = latest.get('cpu_percent', 0) if latest else 0
                mem = latest.get('mem_percent', 0) if latest else 0
                procs = latest.get('processes', 0) if latest else 0
                msg = f'Neural Chan v2.0 | Ready | Agents: 6/6 | CPU: {cpu}% | MEM: {mem}% | Procs: {procs}'
            else:
                msg = 'Neural Chan v2.0 | Ready | Agents: 6/6 | Monitor: offline'
            self.statusbar.showMessage(msg)
        except:
            pass
        self.vpn_label = QLabel('VPN: OFF')
        self.statusbar.addPermanentWidget(self.vpn_label)
        self.mode_label = QLabel('Demo')
        self.statusbar.addPermanentWidget(self.mode_label)
    
    def _setup_system_monitor(self):
        self.system_monitor.start()
        self._cli_log('[SYSTEM] Monitor active: CPU, memory, processes, network', 'green')
    
    def _setup_auto_save(self):
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self._auto_save_tick)
        self.save_timer.start(30000)
    
    def _auto_save_tick(self):
        try:
            self.conversation._save()
            self.system_monitor._save()
            if self.web_learner:
                self.web_learner._save()
            if self.memory_exporter:
                self.memory_exporter.export_all()
        except:
            pass
    
    def _setup_global_timer(self):
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self._global_tick)
        self.global_timer.start(1000)
    
    def _global_tick(self):
        if self.brain and self.brain.auto_mode:
            status = self.brain.get_status()
            for i, (name, info) in enumerate(status['agents'].items()):
                self.kaomoji.set_agent_active(i, info['status'] == 'working')
    
    def _new_session(self):
        self.cli_output.clear()
        self._cli_log('[SYSTEM] New session', 'green')
    def _export_logs(self):
        self._cli_log('[SYSTEM] Logs exported', 'cyan')
    def _detect_now(self):
        if self.brain:
            self.brain.detection_signal.emit({'threat':'Manual Scan','severity':'Info'})
            self.canvas.pulse_node('detector')
            self.kaomoji.set_mood('Working')
        self._cli_log('[DETECT] Manual scan triggered', 'cyan')
    def _toggle_auto(self):
        if self.brain:
            state = self.brain.toggle_auto()
            self._cli_log(f'[AUTO] {"ON" if state else "OFF"}', 'green' if state else 'red')
            self.kaomoji.auto_btn.setChecked(state)
    def _emergency_stop(self):
        if self.brain: self.brain.stop()
        self.kaomoji.set_mood('Concerned')
        self._cli_log('[EMERGENCY] Halted!', 'red')
        QMessageBox.critical(self, 'EMERGENCY STOP', 'All operations halted. Click Resume to restart.')
    def _resume(self):
        if self.brain: self.brain.resume()
        self.kaomoji.set_mood('Calm')
        self._cli_log('[RESUME] Active', 'green')
    def _launch_tool(self, tool):
        kali_map = {'Nmap':'nmap','Masscan':'masscan','SQLMap':'sqlmap','Metasploit':'msfconsole',
                    'John':'john','Hashcat':'hashcat','Aircrack-ng':'aircrack-ng','Burp Suite':'burpsuite',
                    'Autopsy':'autopsy','Volatility':'volatility','SEToolkit':'setoolkit','Nikto':'nikto'}
        cmd = kali_map.get(tool, 'echo')
        try:
            subprocess.Popen(['x-terminal-emulator', '-e', cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._cli_log(f'[LAUNCH] {tool}', 'green')
        except:
            self._cli_log(f'[ERROR] {tool}', 'red')
    def _on_tool_doubleclick(self, item):
        text = item.text(0).strip()
        if text.startswith('>>'): self._launch_tool(text.replace('>>', '').strip())
    def _show_settings(self):
        self.settings_dock.setVisible(True)
        self._cli_log('[UI] Settings', 'cyan')
    def _toggle_arsenal(self):
        self.arsenal_dock.setVisible(not self.arsenal_dock.isVisible())
    def _show_tickets(self):
        if self.brain: self._cli_log(f'[TICKETS] {self.brain.get_status()["tickets"]}', 'cyan')
    def _show_memory(self):
        if self.brain: self._cli_log(f'[MEMORY] {self.brain.get_status()["patterns"]}', 'purple')
    def _reset_defaults(self):
        self._cli_log('[SYSTEM] Reset', 'green')
    def _on_speak(self, text):
        try:
            self._cli_log(f'[SPEAK] Neural Chan says: {text}', 'purple')
            self.kaomoji.set_mood('Happy')
        except Exception as e:
            print(f'[_ON_SPEAK ERROR] {e}', file=sys.stderr)
    def _cli_log(self, text, color='green'):
        colors = {'green':'#00ff55','red':'#ff0055','cyan':'#00ffff','purple':'#ff00ff','amber':'#ffaa00','white':'#ffffff'}
        self.cli_output.append(f'<span style="color: {colors.get(color, "#00ff55")}">{text}</span>')
    def _cli_execute(self):
        cmd = self.cli_input.text().strip()
        if not cmd: return
        self._cli_log(f'> {cmd}', 'amber')
        self.cli_input.clear()
        parts = cmd.split()
        command = parts[0].lower()
        
        try:
            result = self.conversation.respond(cmd)
        except Exception as e:
            self._cli_log(f'[ERROR] Brain crash: {str(e)[:100]}', 'red')
            self.kaomoji.set_mood('Concerned')
            return
        
        self._cli_log(f'[NEURAL] {result["response"]}', 'cyan')
        self.kaomoji.set_mood(result['mood'])
        
        if result.get('new_words_learned'):
            words_str = ', '.join(result['new_words_learned'])
            self._cli_log(f'[LEARN] New words: {words_str} (+{len(result["new_words_learned"])} | Total: {result["total_words"]})', 'purple')
        
        if self.conversation.vocab['total_conversations'] % 5 == 0:
            self._cli_log(f'[PROFICIENCY] {result["proficiency"]}% | Chats: {self.conversation.vocab["total_conversations"]}', 'green')
        
        intent = result['intent']
        
        if intent == 'detect' or command == 'detect':
            self._detect_now()
        elif intent == 'status' or command == 'status':
            if self.brain:
                s = self.brain.get_status()
                self._cli_log(f'[STATUS] Auto={s["auto"]} Tix={s["tickets"]} Pat={s["patterns"]}', 'cyan')
        elif intent == 'agents' or command == 'agents':
            if self.brain:
                for name, info in self.brain.agents.items(): 
                    self._cli_log(f'  {name}: {info["status"]}', 'cyan')
        elif intent == 'tickets' or command == 'tickets':
            self._show_tickets()
        elif intent == 'memory' or command == 'memory':
            self._show_memory()
        elif intent == 'patterns' or command == 'patterns':
            if self.brain:
                for p in self.brain.patterns: self._cli_log(f'  {p}', 'purple')
        elif intent == 'stop' or command == 'stop':
            self._emergency_stop()
        elif intent == 'resume' or command == 'resume':
            self._resume()
        elif command == 'clear':
            self.cli_output.clear()
        elif intent == 'speak' or command == 'speak':
            text = ' '.join(parts[1:]) if len(parts) > 1 else result['response']
            self.kaomoji.speak(text)
        elif command == 'theme':
            color = parts[1] if len(parts) > 1 else 'crimson'
            self._cli_log(f'Theme: {color}', 'cyan')
        elif command == 'help':
            self._cli_log('Commands: detect status agents tickets memory patterns stop resume clear speak theme', 'cyan')
            self._cli_log('Chat: hello who are you what can you do joke time motivate me search <topic> system', 'cyan')
        elif command.startswith('name '):
            name = cmd[5:].strip()
            msg = self.conversation.set_user_name(name)
            self._cli_log(f'[NEURAL] {msg}', 'green')
        elif command == 'stats':
            stats = self.conversation.get_stats()
            self._cli_log(f'[STATS] Proficiency: {stats.get("proficiency",0)}% | Words: {stats.get("words_learned",0)} | Chats: {stats.get("conversations",0)} | Facts: {stats.get("facts",0)} | Mood: {stats.get("mood","?")}', 'green')
        elif command == 'export' or command == 'memory':
            if self.memory_exporter:
                files = self.memory_exporter.export_all()
                for f in files:
                    self._cli_log(f'[MEMORY] {f}', 'green')
                self._cli_log(f'[MEMORY] {len(files)} files saved to ~/neural-chan/memory/', 'green')
            else:
                self._cli_log('[MEMORY] Exporter not loaded', 'red')
            return
            self._cli_log(f'[STATS] Proficiency: {stats.get("proficiency",0)}% | Words: {stats.get("words_learned",0)} | Chats: {stats.get("conversations",0)} | Facts: {stats.get("facts",0)} | Mood: {stats.get("mood","?")}', 'green')
        elif command == 'webstats':
            if self.web_learner:
                ws = self.web_learner.get_stats()
                self._cli_log(f'[WEB] Cached: {ws["cached_topics"]} | Hits: {ws["cache_hits"]} | Misses: {ws["cache_misses"]} | Hit rate: {ws["hit_rate"]}%', 'cyan')
        elif command == 'sysinfo':
            if self.system_monitor:
                latest = self.system_monitor.get_latest()
                if latest:
                    self._cli_log(f'[SYS] CPU: {latest.get("cpu_percent",0)}% | MEM: {latest.get("mem_percent",0)}% | Procs: {latest.get("processes",0)} | Load: {latest.get("load_1m",0)}', 'cyan')
                    if latest.get('top_processes'):
                        for p in latest['top_processes']:
                            self._cli_log(f'  {p["name"]} (PID {p["pid"]}): {p["cpu"]}% CPU', 'cyan')
    def set_brain(self, brain):
        self.brain = brain
        brain.log_signal.connect(self._on_brain_log)
        brain.status_signal.connect(self._on_brain_status)
        brain.detection_signal.connect(self._on_detection)
    def _on_brain_log(self, msg, color): self._cli_log(msg, color)
    def _on_brain_status(self, status): self.statusbar.showMessage(f'Neural Chan v1.5.1 | {status}')
    def _on_detection(self, det):
        try:
            self.canvas.pulse_node('detector')
            self.kaomoji.set_mood('Alert')
            self._cli_log(f'[ALERT] {det["threat"]} | {det["severity"]}', 'red')
        except Exception as e:
            print(f'[_ON_DETECTION ERROR] {e}', file=sys.stderr)
