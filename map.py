
import sys
import math
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from serial_manager import SerialManager


# ================= HTML MAP =================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Rocket GPS Tracker</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
html, body, #map {
    height: 100%;
    margin: 0;
    padding: 0;
}
</style>
</head>

<body>
<div id="map"></div>

<script>
var map = L.map('map').setView([0, 0], 2);   // 🌍 world view

L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  { maxZoom: 23 }
).addTo(map);

var marker = null;
var path = L.polyline([], { color: 'cyan', weight: 3 }).addTo(map);

function updatePosition(lat, lon) {
    if (!marker) {
        marker = L.marker([lat, lon]).addTo(map);
        map.setView([lat, lon], 18);
    } else {
        marker.setLatLng([lat, lon]);
    }

    path.addLatLng([lat, lon]);
    map.panTo([lat, lon], { animate: true, duration: 0.5 });
}
</script>
</body>
</html>
"""



# ================= DISTANCE =================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ================= MAP WINDOW =================
class MapWindow(QtWidgets.QWidget):
    def __init__(self, serial_manager=None):
        super().__init__()

        self.serial_manager = serial_manager or SerialManager()
        self.serial_manager.data_received.connect(self.on_telemetry_received)

        self.lat = None
        self.lon = None
        self.altitude = 0.0
        self.speed = 0.0

        self.last_lat = None
        self.last_lon = None
        self.last_time = None

        self.page_ready = False

        self.setWindowTitle("Satellite GPS Tracker")
        self.resize(1280, 750)

        layout = QtWidgets.QVBoxLayout(self)

        self.map_view = QWebEngineView()
        self.map_view.setHtml(HTML_TEMPLATE)
        self.map_view.loadFinished.connect(self.on_map_loaded)
        layout.addWidget(self.map_view)

        # ---------- INFO PANEL ----------
        self.info_frame = QtWidgets.QFrame(self)
        self.info_frame.setGeometry(20, 20, 260, 120)
        self.info_frame.raise_()

        info_layout = QtWidgets.QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(12, 12, 12, 12)

        self.speed_card = QtWidgets.QLabel("Speed: 0.00 m/s")
        self.altitude_card = QtWidgets.QLabel("Altitude: 0.0 m")

        info_layout.addWidget(self.speed_card)
        info_layout.addWidget(self.altitude_card)

        self.setStyleSheet("""
        QWidget { background: #1b1b2f; }
        QFrame {
            background: rgba(20,20,40,0.85);
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.4);
        }
        QLabel {
            color: white;
            font: 12pt "Segoe UI";
        }
        """)

    # ================= MAP READY =================
    def on_map_loaded(self):
        self.page_ready = True
        self.map_view.page().runJavaScript("""
            if (typeof marker !== 'undefined' && marker !== null) {
                map.removeLayer(marker);
                marker = null;
            }
            path.setLatLngs([]);
            map.setView([0,0],2);
        """)
        print("[MapWindow] Map reset & loaded")

    # ================= CSV TELEMETRY PARSER =================
    @pyqtSlot(str)
    def on_telemetry_received(self, line):
        try:
            parts = line.strip().split(",")

            # Minimum required fields check (safer than strict ==)
            if len(parts) < 9:
                return

            # Parse safely
            try:
                altitude = float(parts[3])
                new_lat = float(parts[7])
                new_lon = float(parts[8])
            except ValueError:
                return

            # Ignore invalid GPS
            if new_lat == 0.0 or new_lon == 0.0:
                return

            now = time.time()

            # -------- SPEED CALCULATION --------
            if self.last_lat is None:
                self.speed = 0.0
            else:
                dt = now - self.last_time
                if dt > 0:
                    dist = haversine(self.last_lat, self.last_lon, new_lat, new_lon)

                    # Ignore unrealistic jumps (> 200 m in 1s)
                    if dist < 200:
                        self.speed = dist / dt

            self.last_lat = new_lat
            self.last_lon = new_lon
            self.last_time = now

            self.altitude = altitude
            self.lat = new_lat
            self.lon = new_lon

            # -------- UI UPDATE --------
            self.speed_card.setText(f"Speed: {self.speed:.2f} m/s")
            self.altitude_card.setText(f"Altitude: {self.altitude:.1f} m")

            # -------- MAP UPDATE --------
            if self.page_ready:
                self.map_view.page().runJavaScript(
                    f"updatePosition({self.lat}, {self.lon});"
                )

        except Exception as e:
            print("[MapWindow] Parse error:", e)
            print("Raw line:", line)
# ================= MAIN =================
'''if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())'''
