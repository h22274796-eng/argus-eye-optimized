import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path="data/argus_eye.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detection_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE,
                    image_path TEXT,
                    detections_count INTEGER,
                    detections TEXT,
                    processing_time REAL,
                    lat REAL,
                    lon REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Проверка наличия колонок (если БД уже создана)
            try: cursor.execute('ALTER TABLE detection_tasks ADD COLUMN lat REAL')
            except: pass
            try: cursor.execute('ALTER TABLE detection_tasks ADD COLUMN lon REAL')
            except: pass
            conn.commit()

    def save_detection_task(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO detection_tasks 
                (task_id, image_path, detections_count, detections, processing_time, lat, lon)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['task_id'], 
                data['image_path'], 
                data['detections_count'], 
                str(data['detections']), 
                data.get('processing_time', 0),
                data.get('lat'), 
                data.get('lon')
            ))
            conn.commit()

    def get_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM detection_tasks ORDER BY timestamp DESC')
            return [dict(row) for row in cursor.fetchall()]

db = Database()