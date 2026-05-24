"""Neural Window — Main PyQt6 GUI for Neural Chan OS v2.5"""
import os, sys, random, subprocess
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFrame, QProgressBar,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from neural_canvas import NeuralCanvas
from kaomoji_widget import KaomojiWidget
from neural_conversation_v2 import NeuralConversationV2
from system_monitor import SystemMonitor
from web_learner import WebLearner
from memory_exporter import MemoryExporter

class NeuralWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Neural Chan OS v2.5 — SELF-LEARNING')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet('background-color: #0a0a0a; color: #e0e0e0;')
        
        self.system_monitor = SystemMonitor()
        self.web_learner = WebLearner()
        self.memory_exporter = MemoryExporter()
        self.conversation = NeuralConversationV2(
            system_monitor=self.system_monitor,
            web_learner=self.web_learner
        )
        self.system_monitor.start()
        
        self._setup_ui()
        self._setup_timers()
        
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header
        header = QLabel('◕‿◕ NEURAL CHAN OS v2.5')
        header.setFont(QFont('Courier', 16, QFont.Weight.Bold))
        header.setStyleSheet('color: #ff0033; padding: 4px;')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Top splitter: Kaomoji + Canvas
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Kaomoji panel
        kaomoji_container = QFrame()
        kaomoji_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 8px; background: #08080c; }')
        kaomoji_layout = QVBoxLayout(kaomoji_container)
        kaomoji_layout.setContentsMargins(4, 4, 4, 4)
        self.kaomoji = KaomojiWidget()
        self.kaomoji.setMinimumSize(340, 280)
        self.kaomoji.speak_signal.connect(self._on_speak)
        self.kaomoji.mood_signal.connect(self._on_mood_change)
        kaomoji_layout.addWidget(self.kaomoji, 1)
        top_splitter.addWidget(kaomoji_container)
        
        # Right: Neural canvas
        canvas_container = QFrame()
        canvas_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 8px; background: #050508; }')
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(2, 2, 2, 2)
        self.canvas = NeuralCanvas()
        self.canvas.setMinimumSize(500, 350)
        canvas_layout.addWidget(self.canvas, 1)
        top_splitter.addWidget(canvas_container)
        
        top_splitter.setSizes([420, 700])
        layout.addWidget(top_splitter, 2)
        
        # Connect canvas to brain data after init
        QTimer.singleShot(1000, self._connect_canvas_data)
        
        # CLI area
        cli_frame = QFrame()
        cli_frame.setStyleSheet('QFrame { border: 1px solid #1a1a1a; border-radius: 6px; background: #0d0d12; }')
        cli_layout = QVBoxLayout(cli_frame)
        cli_layout.setContentsMargins(6, 6, 6, 6)
        cli_layout.setSpacing(4)
        
        # Quick buttons
        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(4)
        for label, cmd in [
            ('DETECT', 'detect'), ('STATUS', 'status'), ('AGENTS', 'agents'),
            ('TICKETS', 'tickets'), ('MEMORY', 'memory'), ('PATTERNS', 'patterns'),
            ('STOP', 'stop'), ('RESUME', 'resume'), ('CLEAR', 'clear')
        ]:
            btn = QPushButton(label)
            btn.setFont(QFont('Courier', 8, QFont.Weight.Bold))
            color = '#ff4444' if label == 'STOP' else '#ff0033'
            btn.setStyleSheet(f'QPushButton {{ background: #1a1a1a; color: {color}; border: 1px solid {color}; border-radius: 3px; padding: 4px; }} QPushButton:hover {{ background: #330000; }}')
            btn.clicked.connect(lambda checked, c=cmd: self._cli_execute(c))
            btn_row1.addWidget(btn)
        cli_layout.addLayout(btn_row1)
        
        # CLI output
        self.cli_output = QTextEdit()
        self.cli_output.setReadOnly(True)
        self.cli_output.setFont(QFont('Courier', 10))
        self.cli_output.setStyleSheet('QTextEdit { background: #0a0a0a; color: #e0e0e0; border: 1px solid #1a1a1a; border-radius: 4px; }')
        self.cli_output.setMaximumHeight(200)
        cli_layout.addWidget(self.cli_output, 1)
        
        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(6)
        self.cli_input = QLineEdit()
        self.cli_input.setFont(QFont('Courier', 11))
        self.cli_input.setStyleSheet('QLineEdit { background: #1a1a1a; color: #e0e0e0; border: 1px solid #333; border-radius: 4px; padding: 6px; } QLineEdit:focus { border-color: #ff0033; }')
        self.cli_input.setPlaceholderText('Enter command...')
        self.cli_input.returnPressed.connect(self._on_enter)
        input_row.addWidget(self.cli_input, 1)
        
        send_btn = QPushButton('SEND')
        send_btn.setFont(QFont('Courier', 10, QFont.Weight.Bold))
        send_btn.setStyleSheet('QPushButton { background: #330000; color: #ff0033; border: 1px solid #ff0033; border-radius: 4px; padding: 6px 14px; } QPushButton:hover { background: #550000; } QPushButton:pressed { background: #ff0033; color: #000; }')
        send_btn.clicked.connect(self._on_enter)
        input_row.addWidget(send_btn)
        cli_layout.addLayout(input_row)
        
        # Bottom buttons
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(4)
        for label, cmd, color in [
            ('SET', 'set', '#ff6600'), ('ARS', 'ars', '#ff0033'),
            ('SCN', 'scn', '#00ff55'), ('TKT', 'tkt', '#00ccff'),
            ('MEM', 'mem', '#ff00ff'), ('AUT', 'auto', '#ffff00')
        ]:
            btn = QPushButton(label)
            btn.setFont(QFont('Courier', 8, QFont.Weight.Bold))
            btn.setStyleSheet(f'QPushButton {{ background: #1a1a1a; color: {color}; border: 1px solid {color}; border-radius: 3px; padding: 4px; }} QPushButton:hover {{ background: #330000; }}')
            btn.clicked.connect(lambda checked, c=cmd: self._cli_execute(c))
            btn_row2.addWidget(btn)
        cli_layout.addLayout(btn_row2)
        
        layout.addWidget(cli_frame, 1)
        
        # Status bar
        self.status_bar = QLabel('VPN: OFF | Demo | Neural Chan Ready')
        self.status_bar.setFont(QFont('Courier', 9))
        self.status_bar.setStyleSheet('color: #666; padding: 2px;')
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_bar)
        
        self._cli_log('[SYS] Neural Chan OS v2.5 initialized', 'green')
        self._cli_log('[SYS] Type "help" for commands, "stats" for brain status', 'green')

    def _connect_canvas_data(self):
        try:
            if hasattr(self, 'canvas') and hasattr(self, 'conversation'):
                self.canvas.set_data_source(self.conversation)
                self._cli_log('[CANVAS] Connected to brain data — nodes represent real vocabulary', 'cyan')
            if hasattr(self, 'canvas') and hasattr(self, 'system_monitor'):
                self.canvas.set_system_monitor(self.system_monitor)
        except Exception as e:
            self._cli_log(f'[CANVAS] Data connection failed: {e}', 'yellow')

    def _setup_timers(self):
        self.auto_save = QTimer(self)
        self.auto_save.timeout.connect(self._auto_save_tick)
        self.auto_save.start(30000)
        
        self.sys_refresh = QTimer(self)
        self.sys_refresh.timeout.connect(self._refresh_status)
        self.sys_refresh.start(2000)

    def _refresh_status(self):
        try:
            if self.system_monitor:
                latest = self.system_monitor.get_latest()
                if latest:
                    cpu = latest.get('cpu_percent', 0)
                    mem = latest.get('mem_percent', 0)
                    self.status_bar.setText(f'CPU: {cpu}% | MEM: {mem}% | VPN: OFF | Demo')
        except:
            pass

    def _auto_save_tick(self):
        try:
            self.conversation._save()
            self.system_monitor._save()
            if self.web_learner:
                self.web_learner._save()
            if hasattr(self, 'memory_exporter') and self.memory_exporter:
                self.memory_exporter.export_all()
        except:
            pass

    def _on_enter(self):
        text = self.cli_input.text().strip()
        if not text:
            return
        self.cli_input.clear()
        self._cli_execute(text)

    def _cli_log(self, text, color='white'):
        colors = {
            'white': '#e0e0e0', 'green': '#00ff55', 'red': '#ff4444',
            'purple': '#ff00ff', 'cyan': '#00ccff', 'yellow': '#ffaa00',
            'orange': '#ff6600'
        }
        c = colors.get(color, '#e0e0e0')
        ts = datetime.now().strftime('%H:%M:%S')
        self.cli_output.append(f'<span style="color:#666;">{ts}</span> <span style="color:{c};">{text}</span>')
        self.cli_output.verticalScrollBar().setValue(self.cli_output.verticalScrollBar().maximum())

    def _on_speak(self, text):
        try:
            self._cli_log(f'[SPEAK] Neural Chan says: {text}', 'purple')
            self.kaomoji.set_mood('Happy')
        except Exception as e:
            print(f'[_ON_SPEAK ERROR] {e}', file=sys.stderr)

    def _on_mood_change(self, mood):
        try:
            self._cli_log(f'[MOOD] Changed to {mood}', 'cyan')
        except:
            pass

    def _cli_execute(self, command):
        text = command.strip()
        self._cli_log(f'> {text}', 'white')
        
        try:
            result = self.conversation.respond(text)
            response = result.get('response', 'No response')
            intent = result.get('intent', 'unknown')
            mood = result.get('mood', 'Calm')
            
            # Color by intent
            color_map = {
                'greeting': 'green', 'farewell': 'green', 'gratitude': 'green',
                'joke': 'purple', 'motivation': 'cyan', 'praise': 'cyan',
                'negative': 'red', 'error': 'red', 'stop': 'red',
                'system': 'orange', 'detect': 'orange', 'auto': 'orange',
                'search': 'cyan', 'learning': 'cyan', 'definition': 'cyan',
                'stats': 'green', 'export': 'green', 'unknown': 'yellow'
            }
            color = color_map.get(intent, 'white')
            
            self._cli_log(f'[NEURAL] {response}', color)
            self.kaomoji.set_mood(mood)
            
            # Log new words
            new_words = result.get('new_words_learned', [])
            if new_words:
                words_str = ', '.join(new_words)
                self._cli_log(f'[LEARN] New words: {words_str} (+{len(new_words)} | Total: {result["total_words"]})', 'purple')
            
            # Log proficiency
            self._cli_log(f'[PROFICIENCY] {result["proficiency"]}% | Chats: {self.conversation.vocab["conversations"]}', 'green')
            
            # Pulse canvas node if term was looked up
            if intent == 'definition':
                term = text.lower().replace('what is ', '').replace('define ', '').replace('explain ', '').strip().split()[0]
                if hasattr(self, 'canvas'):
                    self.canvas.pulse_node(term)
            
        except Exception as e:
            self._cli_log(f'[ERR] {str(e)}', 'red')
            import traceback
            traceback.print_exc()

    def closeEvent(self, event):
        try:
            self.system_monitor.stop()
            self.conversation._save()
        except:
            pass
        event.accept()

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = NeuralWindow()
    window.show()
    sys.exit(app.exec())
