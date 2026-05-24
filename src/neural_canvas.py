"""Neural Canvas — 3D orbital brain visualization. Nodes = real vocabulary orbiting in a neural ball."""
import math, random, json, os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QFont

DOMAIN_COLORS = {
    'mathematics': QColor(0, 200, 255),
    'computer_science': QColor(0, 255, 100),
    'cybersecurity': QColor(255, 50, 50),
    'kali_linux': QColor(255, 165, 0),
    'programming': QColor(150, 50, 255),
    'general': QColor(200, 200, 200),
    'system': QColor(255, 255, 0),
    'unknown': QColor(100, 100, 100),
}

class DataNode:
    __slots__ = ['x3d','y3d','z3d','vx','vy','vz','radius','pulse','pulse_speed','_x2d','_y2d','_scale','_x2d','_y2d','_scale',
                 'color','label','domain','activity','target_radius','connections','orbit_angle','orbit_speed','orbit_radius']
    def __init__(self, x3d, y3d, z3d, label='node', domain='unknown', radius=5):
        self.x3d = x3d
        self.y3d = y3d
        self.z3d = z3d
        self.vx = random.uniform(-0.1, 0.1)
        self.vy = random.uniform(-0.1, 0.1)
        self.vz = random.uniform(-0.1, 0.1)
        self.radius = radius
        self.pulse = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.03, 0.08)
        self.color = DOMAIN_COLORS.get(domain, DOMAIN_COLORS['unknown'])
        self.label = label
        self.domain = domain
        self.activity = 0.0
        self.target_radius = radius
        self.connections = []
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.orbit_speed = random.uniform(-0.008, 0.008)
        self.orbit_radius = math.sqrt(x3d*x3d + y3d*y3d + z3d*z3d)

class NeuralCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.nodes = []
        self.frame = 0
        self.data_source = None
        self.system_monitor = None
        self.last_vocab_hash = None
        self.active_term = None
        self.rotation_y = 0.0
        self.rotation_x = 0.0
        self.auto_rotate_speed = 0.003
        self._init_placeholder_nodes()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self._sync_brain_data)
        self.data_timer.start(2000)

    def _init_placeholder_nodes(self):
        """Create 60 nodes in a spherical formation."""
        for i in range(60):
            # Fibonacci sphere distribution for even spacing
            phi = math.acos(1 - 2 * (i + 0.5) / 60)
            theta = math.pi * (1 + 5**0.5) * i
            r = random.uniform(80, 200)
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            self.nodes.append(DataNode(x, y, z, f'node-{i}', 'unknown', 4))

    def set_data_source(self, conversation_engine):
        self.data_source = conversation_engine
        self._sync_brain_data()

    def set_system_monitor(self, monitor):
        self.system_monitor = monitor

    def _sync_brain_data(self):
        if not self.data_source:
            return
        try:
            vocab = self.data_source.vocab
            dictionary = vocab.get('dictionary', {})
            domains = vocab.get('domains', {})
            vocab_hash = hash(frozenset(dictionary.keys())) & 0xFFFFFFFF
            if vocab_hash == self.last_vocab_hash:
                return
            self.last_vocab_hash = vocab_hash
            all_terms = list(dictionary.items())
            if len(all_terms) > 60:
                selected = []
                per_domain = max(2, 60 // max(len(domains), 1))
                for domain in domains:
                    domain_terms = [(k,v) for k,v in all_terms if v.get('domain') == domain]
                    selected.extend(random.sample(domain_terms, min(per_domain, len(domain_terms))))
                remaining = [x for x in all_terms if x not in selected]
                if remaining:
                    selected.extend(random.sample(remaining, min(60 - len(selected), len(remaining))))
                all_terms = selected[:60]
            new_nodes = []
            for i, (term, entry) in enumerate(all_terms[:60]):
                phi = math.acos(1 - 2 * (i + 0.5) / max(len(all_terms), 1))
                theta = math.pi * (1 + 5**0.5) * i
                r = random.uniform(60, 180)
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.sin(phi) * math.sin(theta)
                z = r * math.cos(phi)
                domain = entry.get('domain', 'general')
                node = DataNode(x, y, z, term, domain, 5)
                node.orbit_speed = random.uniform(-0.01, 0.01)
                new_nodes.append(node)
            if self.system_monitor:
                try:
                    latest = self.system_monitor.get_latest()
                    if latest and 'top_processes' in latest:
                        for i, proc in enumerate(latest['top_processes'][:5]):
                            phi = random.uniform(0, math.pi)
                            theta = random.uniform(0, 2 * math.pi)
                            r = random.uniform(30, 80)
                            x = r * math.sin(phi) * math.cos(theta)
                            y = r * math.sin(phi) * math.sin(theta)
                            z = r * math.cos(phi)
                            pname = proc.get('name', 'proc')[:12]
                            node = DataNode(x, y, z, pname, 'system', 3)
                            node.orbit_speed = 0.02
                            new_nodes.append(node)
                except:
                    pass
            for i, n1 in enumerate(new_nodes):
                n1.connections = []
                for j, n2 in enumerate(new_nodes):
                    if i != j:
                        dist3d = math.sqrt((n1.x3d-n2.x3d)**2 + (n1.y3d-n2.y3d)**2 + (n1.z3d-n2.z3d)**2)
                        if dist3d < 120 and random.random() < 0.12:
                            n1.connections.append(j)
            self.nodes = new_nodes
        except Exception as e:
            print(f'[CANVAS SYNC ERROR] {e}')

    def pulse_node(self, term_or_index):
        if isinstance(term_or_index, str):
            for node in self.nodes:
                if node.label == term_or_index:
                    node.activity = 1.0
                    node.target_radius = 14
        else:
            if 0 <= term_or_index < len(self.nodes):
                self.nodes[term_or_index].activity = 1.0
                self.nodes[term_or_index].target_radius = 14

    def _project(self, x, y, z):
        """Project 3D point to 2D with perspective."""
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        fov = 400
        if z + fov <= 0:
            z = -fov + 1
        scale = fov / (z + fov)
        return cx + x * scale, cy + y * scale, scale

    def _animate(self):
        self.frame += 1
        self.rotation_y += self.auto_rotate_speed
        self.rotation_x += self.auto_rotate_speed * 0.3
        
        for node in self.nodes:
            # Orbital rotation around center
            node.orbit_angle += node.orbit_speed
            
            # Rotate around Y axis
            cos_y = math.cos(self.rotation_y + node.orbit_angle * 0.5)
            sin_y = math.sin(self.rotation_y + node.orbit_angle * 0.5)
            x_rot = node.x3d * cos_y - node.z3d * sin_y
            z_rot = node.x3d * sin_y + node.z3d * cos_y
            
            # Rotate around X axis
            cos_x = math.cos(self.rotation_x * 0.3)
            sin_x = math.sin(self.rotation_x * 0.3)
            y_rot = node.y3d * cos_x - z_rot * sin_x
            z_final = node.y3d * sin_x + z_rot * cos_x
            
            node._x2d, node._y2d, node._scale = self._project(x_rot, y_rot, z_final)
            
            # Pulse
            node.pulse += node.pulse_speed
            if node.pulse > 2 * math.pi:
                node.pulse -= 2 * math.pi
            
            # Activity decay
            if node.activity > 0:
                node.activity *= 0.97
                node.target_radius = 5 + (node.activity * 10)
            node.radius += (node.target_radius - node.radius) * 0.08
            if abs(node.radius - 5) < 0.5 and node.activity < 0.01:
                node.target_radius = 5
        
        self.update()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w, h = self.width(), self.height()
            painter.fillRect(self.rect(), QColor(5, 0, 8))
            
            # Sort nodes by z-depth (back to front)
            sorted_nodes = sorted(enumerate(self.nodes), key=lambda x: x[1]._scale if hasattr(x[1], '_scale') else 0)
            
            # Draw connections first (behind nodes)
            for idx, node in sorted_nodes:
                for j in node.connections:
                    if j < len(self.nodes):
                        other = self.nodes[j]
                        if hasattr(node, '_x2d') and hasattr(other, '_x2d'):
                            dist = math.sqrt((node._x2d - other._x2d)**2 + (node._y2d - other._y2d)**2)
                            alpha = max(10, int(40 - dist * 0.05))
                            avg_scale = (node._scale + other._scale) / 2
                            pen = QPen(QColor(node.color.red(), node.color.green(), node.color.blue(), int(alpha * avg_scale)), 1)
                            painter.setPen(pen)
                            painter.drawLine(QPointF(node._x2d, node._y2d), QPointF(other._x2d, other._y2d))
            
            # Draw nodes (back to front for proper occlusion)
            for idx, node in sorted_nodes:
                if not hasattr(node, '_x2d'):
                    continue
                    
                x, y = node._x2d, node._y2d
                scale = node._scale
                base_r = node.radius * scale
                
                # Skip if off screen
                if x < -50 or x > w + 50 or y < -50 or y > h + 50:
                    continue
                
                # Depth dimming
                depth_alpha = max(0.3, min(1.0, scale))
                
                # Glow
                glow_r = base_r * (3.0 + 0.8 * abs(math.sin(node.pulse)))
                glow = QRadialGradient(x, y, glow_r)
                glow.setColorAt(0, QColor(node.color.red(), node.color.green(), node.color.blue(), int(60 * depth_alpha)))
                glow.setColorAt(0.5, QColor(node.color.red(), node.color.green(), node.color.blue(), int(20 * depth_alpha)))
                glow.setColorAt(1, QColor(node.color.red(), node.color.green(), node.color.blue(), 0))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow)
                painter.drawEllipse(QPointF(x, y), glow_r, glow_r)
                
                # Core
                core_alpha = int((160 + 95 * abs(math.sin(node.pulse))) * depth_alpha)
                core_color = QColor(node.color.red(), node.color.green(), node.color.blue(), core_alpha)
                painter.setBrush(core_color)
                painter.drawEllipse(QPointF(x, y), base_r, base_r)
                
                # Highlight
                if node.activity > 0.2:
                    hl = QRadialGradient(x - base_r*0.3, y - base_r*0.3, base_r * 0.5)
                    hl.setColorAt(0, QColor(255, 255, 255, int(150 * node.activity * depth_alpha)))
                    hl.setColorAt(1, QColor(255, 255, 255, 0))
                    painter.setBrush(hl)
                    painter.drawEllipse(QPointF(x - base_r*0.3, y - base_r*0.3), base_r*0.5, base_r*0.5)
                
                # Label for active nodes
                if node.activity > 0.3 or base_r > 8:
                    painter.setPen(QColor(255, 255, 255, int(200 * depth_alpha)))
                    painter.setFont(QFont('Courier', max(6, int(7 * scale))))
                    label = node.label[:12]
                    painter.drawText(int(x) - 25, int(y) - base_r - 6, 50, 14, Qt.AlignmentFlag.AlignCenter, label)
            
            # Legend
            painter.setPen(QColor(255, 255, 255, 180))
            painter.setFont(QFont('Courier', 8))
            legend_y = 20
            for domain, color in DOMAIN_COLORS.items():
                if domain in ('unknown', 'system'):
                    continue
                painter.setBrush(color)
                painter.drawRect(10, legend_y, 8, 8)
                painter.drawText(22, legend_y + 8, domain.replace('_', ' ').title())
                legend_y += 14
            
            painter.end()
        except Exception as e:
            print(f'[CANVAS PAINT ERROR] {e}')
