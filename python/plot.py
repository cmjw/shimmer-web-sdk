# Plot sensor data

import json
import threading
import asyncio
import websockets
import pyqtgraph as pg
from collections import deque
from PySide6.QtWidgets import QApplication

MAX_POINTS = 2000

timestamps = deque(maxlen=MAX_POINTS)
gsr = deque(maxlen=MAX_POINTS)

data_lock = threading.Lock()

async def websocket_client():
    print("Connecting to websocket...")
    async with websockets.connect("ws://localhost:8765") as ws:
        print("Connected to ws://localhost:8765")

        async for message in ws:
            try:
                data = json.loads(message)

                if data.get("device") != "shimmer3":
                    continue

                with data_lock:
                    timestamps.append(data["timestamp"]) # will need to change for multiple devices.
                    # need to synchronize with each other, as well as in real time.
                    # shimmer timestamps in ticks

                    gsr.append(data["gsr_cal"])

            except Exception as e:
                print("[ERROR] ", repr(e))

def run_websocket():
    asyncio.run(websocket_client())

app = QApplication([])

# plot in real time
plot = pg.plot(title="Shimmer3 GSR+ Data")
plot.setLabel("left", "GSR")
plot.setLabel("bottom", "Time", "s")

curve = plot.plot()

def update():
    with data_lock:
        if not timestamps:
            return
        if len(timestamps) > 0:
            t = list(timestamps)
            y = list(gsr)

    t0 = t[0]
    #t = [x - t0 for x in t]
    t = [(x - t0) / 32768.0 for x in t] # convert ticks to s

    curve.setData(t, y)

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)

thread = threading.Thread(
    target=run_websocket,
    daemon=True
)
thread.start()

app.exec()