from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QRadialGradient, QLinearGradient, QPen
import subprocess, random, math, sys

class KaomojiWidget(QWidget):
    speak_signal = pyqtSignal(str)
    mood_signal = pyqtSignal(str)
    MOODS = ['Calm','Alert','Working','Learning','Concerned','Happy','Thinking','Offline']
    FACES = {'Calm':'◕‿◕','Alert':'◕_◕','Working':'◕▂◕','Learning':'◕⩊◕',
             'Concerned':'◕︿◕','Happy':'◕‿◕✧','Thinking':'◕‿◉','Offline':'◕_◕'}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 200)
        self.mood = 'Calm'
        self.speaking = False
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, 280), 'y': random.randint(0, 200),
                'vx': random.uniform(-0.8, 0.8), 'vy': random.uniform(-0.8, 0.8),
                'size': random.randint(2, 4), 'alpha': random.randint(40, 160),
                'color': random.choice([QColor(255, 0, 50), QColor(200, 0, 80), QColor(150, 0, 150)]),
                'orbit': random.random() * 2 * math.pi,
                'orbit_speed': random.uniform(0.01, 0.03),
                'orbit_radius': random.randint(40, 100)
            })
        self._setup_ui()
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate)
        self.anim_timer.start(30)
        self.frame = 0
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(3)
        
        # Tiny status
        self.status_label = QLabel('SYSTEM ONLINE')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont('Courier New', 8, QFont.Weight.Bold))
        self.status_label.setStyleSheet('color: #00ff55; background: transparent;')
        self.status_label.setMinimumHeight(12)
        self.status_label.setMaximumHeight(14)
        layout.addWidget(self.status_label)
        
        # FACE — 50% of 130px = 65px
        self.face_label = QLabel(self.FACES['Calm'])
        self.face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.face_label.setStyleSheet('''
            color: #ff0033;
            background: transparent;
            font-family: "DejaVu Sans Mono", "Courier New", monospace;
            font-size: 65px;
            font-weight: bold;
        ''')
        self.face_label.setMinimumHeight(70)
        self.face_label.setMaximumHeight(90)
        self.face_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.face_label, 1)
        
        # Mood row
        mood_layout = QHBoxLayout()
        self.mood_label = QLabel('Calm')
        self.mood_label.setFont(QFont('Courier New', 9))
        self.mood_label.setStyleSheet('color: #ff5555; background: transparent;')
        self.mood_label.setMinimumHeight(12)
        mood_layout.addWidget(self.mood_label)
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(85)
        self.confidence_bar.setTextVisible(False)
        self.confidence_bar.setMaximumHeight(4)
        self.confidence_bar.setStyleSheet('QProgressBar { background: #1a1a1a; border: none; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #330000, stop:1 #ff0033); }')
        mood_layout.addWidget(self.confidence_bar, 1)
        layout.addLayout(mood_layout)
        
        # Voice bars
        self.bars_widget = QWidget()
        self.bars_widget.setMinimumHeight(10)
        self.bars_widget.setMaximumHeight(14)
        bars_layout = QHBoxLayout(self.bars_widget)
        bars_layout.setContentsMargins(0, 0, 0, 0)
        bars_layout.setSpacing(2)
        self.bar_labels = []
        for i in range(12):
            bar = QLabel('▌')
            bar.setStyleSheet('color: #ff0033; font-size: 8px;')
            bars_layout.addWidget(bar)
            self.bar_labels.append(bar)
        layout.addWidget(self.bars_widget)
        
        # Activity LEDs
        activity_layout = QHBoxLayout()
        self.activity_labels = []
        for label_text in ['DET', 'TIX', 'FIX', 'TST', 'LRN', 'COR']:
            lbl = QLabel(label_text)
            lbl.setFont(QFont('Courier New', 8))
            lbl.setStyleSheet('color: #333333; background: transparent;')
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumHeight(12)
            activity_layout.addWidget(lbl)
            self.activity_labels.append(lbl)
        layout.addLayout(activity_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.speak_btn = QPushButton('SPEAK')
        self.speak_btn.setFont(QFont('Courier New', 9, QFont.Weight.Bold))
        self.speak_btn.setMinimumHeight(26)
        self.speak_btn.setStyleSheet('QPushButton { background: #1a1a1a; color: #ff0033; border: 1px solid #ff0033; border-radius: 3px; padding: 3px; } QPushButton:hover { background: #330000; } QPushButton:pressed { background: #ff0033; color: #000000; }')
        self.speak_btn.clicked.connect(self._safe_speak)
        btn_layout.addWidget(self.speak_btn)
        
        self.auto_btn = QPushButton('AUTO')
        self.auto_btn.setFont(QFont('Courier New', 9, QFont.Weight.Bold))
        self.auto_btn.setMinimumHeight(26)
        self.auto_btn.setStyleSheet('QPushButton { background: #1a1a1a; color: #ff0033; border: 1px solid #ff0033; border-radius: 3px; padding: 3px; } QPushButton:hover { background: #330000; } QPushButton:checked { background: #ff0033; color: #000000; }')
        self.auto_btn.setCheckable(True)
        btn_layout.addWidget(self.auto_btn)
        
        self.halt_btn = QPushButton('HALT')
        self.halt_btn.setFont(QFont('Courier New', 9, QFont.Weight.Bold))
        self.halt_btn.setMinimumHeight(26)
        self.halt_btn.setStyleSheet('QPushButton { background: #330000; color: #ff0000; border: 1px solid #ff0000; border-radius: 3px; padding: 3px; } QPushButton:hover { background: #550000; } QPushButton:pressed { background: #ff0000; color: #000000; }')
        btn_layout.addWidget(self.halt_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        try:
            self.cycle_mood()
            self._safe_speak()
        except Exception as e:
            print(f'[KAOMOJI CLICK ERROR] {e}', file=sys.stderr)
    
    def cycle_mood(self):
        try:
            idx = self.MOODS.index(self.mood)
            self.mood = self.MOODS[(idx + 1) % len(self.MOODS)]
            self.face_label.setText(self.FACES[self.mood])
            self.mood_label.setText(self.mood)
            self.mood_signal.emit(self.mood)
            self.confidence_bar.setValue(random.randint(60, 98))
        except Exception as e:
            print(f'[CYCLE MOOD ERROR] {e}', file=sys.stderr)
    
    def set_mood(self, mood):
        try:
            if mood in self.MOODS:
                self.mood = mood
                self.face_label.setText(self.FACES[mood])
                self.mood_label.setText(mood)
                self.confidence_bar.setValue(random.randint(60, 98))
        except Exception as e:
            print(f'[SET MOOD ERROR] {e}', file=sys.stderr)
    
    def set_agent_active(self, agent_idx, active=True):
        try:
            if 0 <= agent_idx < len(self.activity_labels):
                color = '#00ff55' if active else '#333333'
                self.activity_labels[agent_idx].setStyleSheet(f'color: {color}; background: transparent;')
        except:
            pass
    
    def _safe_speak(self, text=None):
        try:
            self.speak(text)
        except Exception as e:
            print(f'[SAFE SPEAK ERROR] {e}', file=sys.stderr)
    
    def speak(self, text=None):
        if text is None:
            text = f"Neural Chan is {self.mood.lower()}. All systems nominal."
        self.speaking = True
        try:
            self.speak_signal.emit(text)
        except Exception as e:
            print(f'[SPEAK SIGNAL ERROR] {e}', file=sys.stderr)
        try:
            subprocess.Popen(['espeak', '-p', '50', '-s', '150', '-v', 'en', text],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f'[ESPEAK ERROR] {e}', file=sys.stderr)
        QTimer.singleShot(2000, self._stop_speaking)
    
    def _stop_speaking(self):
        self.speaking = False
    
    def _animate(self):
        try:
            self.frame += 1
            for i, bar in enumerate(self.bar_labels):
                if self.speaking:
                    height = random.randint(1, 10)
                    base_color = random.choice(['#ff0033', '#ff3366', '#ff6699'])
                else:
                    height = max(1, int(3 * abs(math.sin(self.frame * 0.05 + i * 0.3))))
                    base_color = '#ff0033'
                bar.setText('▌' * height)
                alpha = 100 + int(155 * (height / 10))
                bar.setStyleSheet(f'color: {base_color}; font-size: 8px;')
        except:
            pass
    
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w, h = self.width(), self.height()
            gradient = QRadialGradient(w//2, h//2, max(w, h)//2)
            t = self.frame * 0.01
            gradient.setColorAt(0, QColor(20 + int(10*math.sin(t)), 0, 10 + int(5*math.cos(t))))
            gradient.setColorAt(0.5, QColor(8, 0, 5))
            gradient.setColorAt(1, QColor(3, 0, 2))
            painter.fillRect(self.rect(), gradient)
            
            cx, cy = w // 2, h // 2
            for p in self.particles:
                p['orbit'] += p['orbit_speed']
                px = cx + math.cos(p['orbit']) * p['orbit_radius']
                py = cy + math.sin(p['orbit']) * p['orbit_radius'] * 0.6
                pulse = abs(math.sin(self.frame * 0.03 + p['orbit']))
                alpha = int(50 + 150 * pulse)
                glow = QRadialGradient(px, py, p['size'] * 2)
                glow.setColorAt(0, QColor(p['color'].red(), p['color'].green(), p['color'].blue(), alpha // 2))
                glow.setColorAt(1, QColor(p['color'].red(), p['color'].green(), p['color'].blue(), 0))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow)
                painter.drawEllipse(QPointF(px, py), p['size'] * 2, p['size'] * 2)
                color = QColor(p['color'])
                color.setAlpha(alpha)
                painter.setBrush(color)
                painter.drawEllipse(QPointF(px, py), p['size'], p['size'])
            
            for ring in range(3):
                radius = 50 + ring * 20 + 5 * math.sin(self.frame * 0.02 + ring)
                alpha = int(30 + 40 * abs(math.sin(self.frame * 0.03 + ring * 1.5)))
                painter.setPen(QPen(QColor(255, 0, 50, alpha), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(cx, cy), radius, radius * 0.6)
            
            panel_gradient = QLinearGradient(0, 0, w, h)
            panel_gradient.setColorAt(0, QColor(255, 255, 255, 5))
            panel_gradient.setColorAt(0.5, QColor(255, 255, 255, 2))
            panel_gradient.setColorAt(1, QColor(255, 255, 255, 5))
            painter.setBrush(panel_gradient)
            painter.setPen(QPen(QColor(255, 0, 50, 40), 1))
            painter.drawRoundedRect(6, 6, w-12, h-12, 8, 8)
            
            painter.end()
        except Exception as e:
            print(f'[PAINT ERROR] {e}', file=sys.stderr)
