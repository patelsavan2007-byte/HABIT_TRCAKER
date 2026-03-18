from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    habits = db.relationship("Habit", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Habit(db.Model):
    __tablename__ = "habits"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(10), default="✨")
    color = db.Column(db.String(20), default="#6c5ce7")
    habit_type = db.Column(db.String(20), default="boolean")  # 'boolean' or 'countable'
    target_value = db.Column(db.Float, default=0)  # target for countable habits (e.g. 5 km)
    unit = db.Column(db.String(30), default="")  # unit label (km, glasses, pages, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    completions = db.relationship("HabitCompletion", backref="habit", lazy=True, cascade="all, delete-orphan")

    @property
    def streak(self):
        """Calculate current streak of consecutive days."""
        today = date.today()
        completed_dates = sorted(
            [c.completed_date for c in self.completions],
            reverse=True
        )
        if not completed_dates:
            return 0

        streak = 0
        check_date = today
        for d in completed_dates:
            if d == check_date:
                streak += 1
                check_date = check_date.replace(day=check_date.day - 1) if check_date.day > 1 else date(
                    check_date.year, check_date.month - 1 if check_date.month > 1 else 12,
                    28
                )
            elif d < check_date:
                break
        return streak

    @property
    def completed_today(self):
        today = date.today()
        if self.habit_type == "countable":
            return self.today_value >= self.target_value and self.target_value > 0
        return any(c.completed_date == today for c in self.completions)

    @property
    def today_value(self):
        """Get the logged value for today (countable habits)."""
        today = date.today()
        entry = next((c for c in self.completions if c.completed_date == today), None)
        return entry.value if entry else 0

    @property
    def progress_pct(self):
        """Progress percentage for countable habits (0-100)."""
        if self.habit_type != "countable" or self.target_value <= 0:
            return 100 if self.completed_today else 0
        return min(100, int(self.today_value / self.target_value * 100))

    @property
    def total_completions(self):
        return len(self.completions)


class HabitCompletion(db.Model):
    __tablename__ = "habit_completions"
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    completed_date = db.Column(db.Date, nullable=False, default=date.today)
    value = db.Column(db.Float, default=0)  # logged value for countable habits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("habit_id", "completed_date", name="unique_habit_date"),
    )
