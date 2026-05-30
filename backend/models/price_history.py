"""
Модель истории цен для построения графиков.
"""
from datetime import datetime, timezone

from backend.database.connection import db


class PriceHistory(db.Model):
    """Историческая запись курса валюты или криптовалюты."""

    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_type = db.Column(db.String(20), nullable=False, index=True)  # 'currency' | 'crypto'
    symbol = db.Column(db.String(20), nullable=False, index=True)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    recorded_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    def to_dict(self):
        """Сериализация записи истории в словарь."""
        return {
            'id': self.id,
            'asset_type': self.asset_type,
            'symbol': self.symbol,
            'price': float(self.price),
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }

    def __repr__(self):
        return f'<PriceHistory {self.asset_type}:{self.symbol} @ {self.price}>'
