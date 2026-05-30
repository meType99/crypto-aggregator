"""
Модель таблицы currencies — фиатные валюты.
"""
from datetime import datetime, timezone

from backend.database.connection import db


class Currency(db.Model):
    """Фиатная валюта с актуальным курсом к USD."""

    __tablename__ = 'currencies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True, index=True)
    rate = db.Column(db.Numeric(20, 8), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Сериализация модели в словарь для JSON-ответа."""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'rate': float(self.rate),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Currency {self.code}: {self.rate}>'
