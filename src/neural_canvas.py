from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont, QLinearGradient
import random, math

class NeuralCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 350)
        self.nodes = []
        self.particles = []
        self.connections = []
        self.pulse_nodes = set()
        self.lightning_bolts = []
        self.agent_colors = {
            'detector': QColor(255, 30, 30), 'ticketeer': QColor(30, 144, 255),
            'fixer': QColor(50, 255, 100), 'tester': QColor(255, 215, 0),
            'learner': QColor(186, 85, 211), 'coordinator': QColor(255, 255, 255)
        }
        self._init_network()
        self._init_particles()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)
        self.frame = 0
        self.fps = 60
    
    def _init_network(self):
        cx, cy = self.width() // 2, self.height() // 2
        agents = list(self.agent_colors.keys())
        for i in range(60):
            angle = (i / 60) * 2 * math.pi
            radius = 60 + random.randint(0, 100)
            x = cx + math.cos(angle) * radius + random.randint(-30, 30)
            y = cy + math.sin(angle) * radius + random.randint(-30, 30)
            self.nodes.append({
                'x': x, 'y': y, 'agent': agents[i % 6],
                'size': 3 + random.randint(0, 5), 'pulse': 0,
                'glow_intensity': random.random(),
                'orbit_speed': random.uniform(0.001, 0.003),
                'orbit_angle': angle
            })
        for i, n1 in enumerate(self.nodes):
            for j, n2 in enumerate(self.nodes[i+1:], i+1):
                dist = math.hypot(n1['x']-n2['x'], n1['y']-n2['y'])
                if dist < 140:
                    self.connections.append((i, j, dist))
    
    def _init_particles(self):
        for _ in range(120):
            self.particles.append({
                'x': random.randint(0, 900), 'y': random.randint(0, 700),
                'vx': random.uniform(-0.8, 0.8), 'vy': random.uniform(-0.8, 0.8),
                'size': random.randint(1, 4), 'alpha': random.randint(30, 220),
                'color': random.choice([
                    QColor(255, 0, 60), QColor(220, 0, 80), QColor(180, 0, 120),
                    QColor(255, 50, 100), QColor(200, 50, 150), QColor(255, 100, 50)
                ]),
                'pulse_rate': random.uniform(0.02, 0.06)
            })
    
    def pulse_node(self, agent_type):
        for i, n in enumerate(self.nodes):
            if n['agent'] == agent_type:
                self.pulse_nodes.add(i)
                n['pulse'] = 15
        self._spawn_lightning()
    
    def _spawn_lightning(self):
        for _ in range(3):
            start_x = random.randint(50, self.width()-50)
            start_y = random.randint(50, self.height()-50)
            segments = []
            x, y = start_x, start_y
            for _ in range(random.randint(3, 6)):
                nx = x + random.randint(-40, 40)
                ny = y + random.randint(-40, 40)
                segments.append((x, y, nx, ny))
                x, y = nx, ny
            self.lightning_bolts.append({'segments': segments, 'life': 10, 'max_life': 10})
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        self.frame += 1
        
        # Deep space background
        bg_gradient = QRadialGradient(w//2, h//2, max(w, h))
        bg_gradient.setColorAt(0, QColor(8, 0, 16))
        bg_gradient.setColorAt(0.5, QColor(3, 0, 8))
        bg_gradient.setColorAt(1, QColor(1, 0, 3))
        painter.fillRect(self.rect(), bg_gradient)
        
        # Draw particles with trails
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['x'] < 0: p['x'] = w; p['vx'] = random.uniform(-0.8, 0.8)
            if p['x'] > w: p['x'] = 0; p['vx'] = random.uniform(-0.8, 0.8)
            if p['y'] < 0: p['y'] = h; p['vy'] = random.uniform(-0.8, 0.8)
            if p['y'] > h: p['y'] = 0; p['vy'] = random.uniform(-0.8, 0.8)
            
            pulse = abs(math.sin(self.frame * p['pulse_rate'] + p['x'] * 0.01))
            p['alpha'] = int(40 + 180 * pulse)
            
            # Glow halo
            glow = QRadialGradient(p['x'], p['y'], p['size'] * 3)
            glow.setColorAt(0, QColor(p['color'].red(), p['color'].green(), p['color'].blue(), p['alpha'] // 3))
            glow.setColorAt(1, QColor(p['color'].red(), p['color'].green(), p['color'].blue(), 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'] * 3, p['size'] * 3)
            
            # Core particle
            color = QColor(p['color'])
            color.setAlpha(p['alpha'])
            painter.setBrush(color)
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])
        
        # Draw connections with data flow animation
        for i, j, dist in self.connections:
            n1, n2 = self.nodes[i], self.nodes[j]
            alpha = int(40 + 60 * (1 - dist / 140))
            if i in self.pulse_nodes or j in self.pulse_nodes:
                alpha = min(255, alpha + 150)
            
            # Animated data packet on connection
            flow = (self.frame * 0.02 + i * 0.1) % 1.0
            px = n1['x'] + (n2['x'] - n1['x']) * flow
            py = n1['y'] + (n2['y'] - n1['y']) * flow
            
            color = QColor(255, 0, 50)
            color.setAlpha(alpha)
            painter.setPen(QPen(color, 0.8))
            painter.drawLine(QPointF(n1['x'], n1['y']), QPointF(n2['x'], n2['y']))
            
            # Data packet dot
            if alpha > 80:
                packet_color = QColor(255, 100, 100, 200)
                painter.setBrush(packet_color)
                painter.drawEllipse(QPointF(px, py), 2, 2)
        
        # Draw nodes with orbital glow
        for i, n in enumerate(self.nodes):
            color = self.agent_colors[n['agent']]
            
            # Orbital glow
            n['glow_intensity'] += n['orbit_speed']
            glow_radius = 12 + 8 * abs(math.sin(n['glow_intensity']))
            glow = QRadialGradient(n['x'], n['y'], glow_radius)
            glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 80))
            glow.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 30))
            glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            painter.setBrush(glow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(n['x'], n['y']), glow_radius, glow_radius)
            
            if n['pulse'] > 0:
                n['pulse'] -= 0.2
                pulse_glow = QRadialGradient(n['x'], n['y'], 25 + n['pulse'])
                pulse_glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 255))
                pulse_glow.setColorAt(0.3, QColor(color.red(), color.green(), color.blue(), 150))
                pulse_glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
                painter.setBrush(pulse_glow)
                painter.drawEllipse(QPointF(n['x'], n['y']), 25 + n['pulse'], 25 + n['pulse'])
            
            # Node core
            painter.setBrush(color)
            painter.setPen(QPen(QColor(255, 255, 255, 100), 0.5))
            painter.drawEllipse(QPointF(n['x'], n['y']), n['size'], n['size'])
        
        # Lightning bolts
        for bolt in self.lightning_bolts[:]:
            bolt['life'] -= 1
            if bolt['life'] <= 0:
                self.lightning_bolts.remove(bolt)
                continue
            alpha = int(255 * (bolt['life'] / bolt['max_life']))
            painter.setPen(QPen(QColor(255, 255, 200, alpha), 2))
            for x1, y1, x2, y2 in bolt['segments']:
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            painter.setPen(QPen(QColor(255, 255, 255, alpha), 1))
            for x1, y1, x2, y2 in bolt['segments']:
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Scanline CRT overlay
        for y in range(0, h, 3):
            alpha = int(8 * abs(math.sin(y * 0.08 + self.frame * 0.015)))
            painter.setPen(QPen(QColor(255, 0, 50, alpha), 1))
            painter.drawLine(0, y, w, y)
        
        # Vignette
        vignette = QRadialGradient(w//2, h//2, max(w, h) * 0.7)
        vignette.setColorAt(0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.7, QColor(0, 0, 0, 80))
        vignette.setColorAt(1, QColor(0, 0, 0, 180))
        painter.setBrush(vignette)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, w, h)
        
        # HUD overlay
        painter.setPen(QColor(255, 0, 50, 200))
        painter.setFont(QFont('Courier', 9, QFont.Weight.Bold))
        hud_text = f'NODES: {len(self.nodes)}  SYNAPSES: {len(self.connections)}  AGENTS: 6  FPS: {self.fps}'
        painter.drawText(15, 25, hud_text)
        
        # Corner brackets
        bracket_color = QColor(255, 0, 50, 150)
        painter.setPen(QPen(bracket_color, 2))
        bracket_size = 20
        painter.drawLine(5, 5, 5 + bracket_size, 5)
        painter.drawLine(5, 5, 5, 5 + bracket_size)
        painter.drawLine(w-5, 5, w-5-bracket_size, 5)
        painter.drawLine(w-5, 5, w-5, 5 + bracket_size)
        painter.drawLine(5, h-5, 5 + bracket_size, h-5)
        painter.drawLine(5, h-5, 5, h-5-bracket_size)
        painter.drawLine(w-5, h-5, w-5-bracket_size, h-5)
        painter.drawLine(w-5, h-5, w-5, h-5-bracket_size)
        
        painter.end()
    
    def resizeEvent(self, event):
        self.nodes = []; self.connections = []; self._init_network(); super().resizeEvent(event)
