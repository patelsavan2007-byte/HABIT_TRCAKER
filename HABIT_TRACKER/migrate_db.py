"""
Migration script: Add missing columns for countable habits feature.
- habits.habit_type
- habits.target_value
- habits.unit
- habit_completions.value
"""
import sqlite3

DB_PATH = "instance/habitu.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns for habits table
    cursor.execute("PRAGMA table_info(habits)")
    habit_cols = [row[1] for row in cursor.fetchall()]
    print(f"Current habits columns: {habit_cols}")

    # Add missing columns to habits
    if "habit_type" not in habit_cols:
        cursor.execute('ALTER TABLE habits ADD COLUMN habit_type VARCHAR(20) DEFAULT "boolean"')
        print("  + Added habit_type column")

    if "target_value" not in habit_cols:
        cursor.execute("ALTER TABLE habits ADD COLUMN target_value FLOAT DEFAULT 0")
        print("  + Added target_value column")

    if "unit" not in habit_cols:
        cursor.execute('ALTER TABLE habits ADD COLUMN unit VARCHAR(30) DEFAULT ""')
        print("  + Added unit column")

    # Get existing columns for habit_completions table
    cursor.execute("PRAGMA table_info(habit_completions)")
    completion_cols = [row[1] for row in cursor.fetchall()]
    print(f"\nCurrent habit_completions columns: {completion_cols}")

    if "value" not in completion_cols:
        cursor.execute("ALTER TABLE habit_completions ADD COLUMN value FLOAT DEFAULT 0")
        print("  + Added value column")

    conn.commit()
    conn.close()
    print("\nMigration complete!")

if __name__ == "__main__":
    migrate()
