"""
Модель таблицы cryptocurrencies — криптовалюты.
"""
from datetime import datetime, timezone

from backend.database.connection import db


class Cryptocurrency(db.Model):
    """Криптовалюта с актуальной ценой в USD."""

    __tablename__ = 'cryptocurrencies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), nullable=False, unique=True, index=True)
    price = db.Column(db.Numeric(20, 8), nullable=False)
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
            'symbol': self.symbol,
            'price': float(self.price),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Cryptocurrency {self.symbol}: {self.price}>'
