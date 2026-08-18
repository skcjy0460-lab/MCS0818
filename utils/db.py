# -*- coding: utf-8 -*-
"""로컬 SQLite 저장소.
※ 병원 이름 / 직원 명단 / 병원 내부정보는 저장하지 않습니다.
저장 대상은 사용자가 이 시스템 사용 편의를 위해 남기는 즐겨찾기, 개인 일정(자체 관리용 라벨),
완료 체크 상태, 알림 설정값뿐입니다.
"""
import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "medium_compliance.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            title TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(section, record_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            title TEXT NOT NULL,
            event_type TEXT NOT NULL,
            memo TEXT,
            legal INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS event_completion (
            event_key TEXT PRIMARY KEY,
            completed INTEGER DEFAULT 0,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            event_key TEXT PRIMARY KEY,
            days_before TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------- 즐겨찾기 ----------
def is_favorite(section, record_id):
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM favorites WHERE section=? AND record_id=?", (section, record_id)).fetchone()
    conn.close()
    return row is not None


def toggle_favorite(section, record_id, title):
    conn = get_conn()
    if is_favorite(section, record_id):
        conn.execute("DELETE FROM favorites WHERE section=? AND record_id=?", (section, record_id))
        state = False
    else:
        conn.execute("INSERT OR IGNORE INTO favorites (section, record_id, title) VALUES (?,?,?)",
                     (section, record_id, title))
        state = True
    conn.commit()
    conn.close()
    return state


def list_favorites():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM favorites ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- 개인(자체) 일정 ----------
def add_custom_event(event_date, title, event_type, memo="", legal=False):
    conn = get_conn()
    conn.execute(
        "INSERT INTO custom_events (event_date, title, event_type, memo, legal) VALUES (?,?,?,?,?)",
        (event_date.isoformat() if isinstance(event_date, date) else event_date, title, event_type, memo, int(legal)),
    )
    conn.commit()
    conn.close()


def list_custom_events():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM custom_events ORDER BY event_date ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_custom_event(event_id):
    conn = get_conn()
    conn.execute("DELETE FROM custom_events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()


def toggle_custom_event_complete(event_id):
    conn = get_conn()
    row = conn.execute("SELECT completed FROM custom_events WHERE id=?", (event_id,)).fetchone()
    new_val = 0 if (row and row["completed"]) else 1
    conn.execute("UPDATE custom_events SET completed=? WHERE id=?", (new_val, event_id))
    conn.commit()
    conn.close()
    return bool(new_val)


# ---------- 법정일정 완료 체크 ----------
def get_completion(event_key):
    conn = get_conn()
    row = conn.execute("SELECT completed FROM event_completion WHERE event_key=?", (event_key,)).fetchone()
    conn.close()
    return bool(row["completed"]) if row else False


def set_completion(event_key, completed: bool):
    conn = get_conn()
    conn.execute(
        "INSERT INTO event_completion (event_key, completed, updated_at) VALUES (?,?,datetime('now'))"
        " ON CONFLICT(event_key) DO UPDATE SET completed=excluded.completed, updated_at=excluded.updated_at",
        (event_key, int(completed)),
    )
    conn.commit()
    conn.close()


# ---------- 알림 설정 ----------
def set_notification(event_key, days_before_list):
    conn = get_conn()
    val = ",".join(str(d) for d in days_before_list)
    conn.execute(
        "INSERT INTO notification_settings (event_key, days_before) VALUES (?,?)"
        " ON CONFLICT(event_key) DO UPDATE SET days_before=excluded.days_before",
        (event_key, val),
    )
    conn.commit()
    conn.close()


def get_notification(event_key):
    conn = get_conn()
    row = conn.execute("SELECT days_before FROM notification_settings WHERE event_key=?", (event_key,)).fetchone()
    conn.close()
    if row and row["days_before"]:
        return [int(x) for x in row["days_before"].split(",") if x]
    return []
