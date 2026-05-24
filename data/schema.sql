-- data/schema.sql
-- Run with: sqlite3 data/nihongo.db < data/schema.sql

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- One row per vocabulary item.
CREATE TABLE IF NOT EXISTS cards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    front       TEXT NOT NULL,         -- Japanese (kanji + kana, e.g. "朝（あさ）")
    back        TEXT NOT NULL,         -- English meaning(s)
    reading     TEXT,                  -- kana-only reading, optional
    example     TEXT,                  -- example sentence
    tags        TEXT,                  -- comma-separated, e.g. "n5,time"
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One row per card per user (we have one user, but designing for the future).
-- Tracks the *current* state of the card in the scheduler.
CREATE TABLE IF NOT EXISTS card_state (
    card_id          INTEGER PRIMARY KEY REFERENCES cards(id) ON DELETE CASCADE,
    stability        REAL NOT NULL DEFAULT 1.0,    -- days; higher = more durable memory
    difficulty       REAL NOT NULL DEFAULT 5.0,    -- 1..10; higher = harder for you
    due_at           TEXT NOT NULL DEFAULT (datetime('now')),
    last_reviewed_at TEXT,
    reps             INTEGER NOT NULL DEFAULT 0,   -- total times reviewed
    lapses           INTEGER NOT NULL DEFAULT 0    -- times you said "Again"
);

-- Append-only log. Never updated, only inserted. Lets you replay history,
-- retrain the scheduler later, or analyze your learning curve.
CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id     INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    rating      INTEGER NOT NULL CHECK (rating IN (1,2,3,4)),  -- 1=Again,2=Hard,3=Good,4=Easy
    reviewed_at TEXT NOT NULL DEFAULT (datetime('now')),
    elapsed_days REAL,                  -- days since previous review
    stability_before REAL,
    stability_after  REAL,
    difficulty_before REAL,
    difficulty_after  REAL
);

CREATE INDEX IF NOT EXISTS idx_card_state_due ON card_state(due_at);
CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id, reviewed_at);