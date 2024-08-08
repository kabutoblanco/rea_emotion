import time
import threading

from db import ConexionSQLite

class Record(threading.Thread):
    def __init__(self, queue, sleep, rate=5, stop=False):
        super().__init__()
        self.queue = queue
        self.sleep = sleep
        self.rate = rate
        self.stop_ = stop
        self.conexion = ConexionSQLite()
        self.records = []
        self.time_prev = time.time()

    def run(self):
        while True:
            if not self.queue.empty():
                data = self.queue.get()
                self.records.append(data)
            if time.time() - self.time_prev > self.rate and len(self.records) > 0:
                self.conexion.insert('INSERT INTO sesion_detail(sesion_id, ang, dis, fea, hap, sad, sur, neu, blink_rate, pos_head, xp, yp, is_engagement, is_close_eyes, is_blink, rea_pos, rea_action, rea_media, time_absolute, time_relative) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', self.records, multiply=True)
                print(f"Registrado en la base de datos: {len(self.records)}")
                self.records = []
                self.time_prev = time.time()

            if self.queue.empty() and not self.records and self.stop_: 
                break

            time.sleep(self.sleep)
    
    def stop(self):
        self.stop_ = True