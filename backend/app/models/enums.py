from enum import Enum


class BackupFrequency(str, Enum):
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TableShape(str, Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    RECTANGLE_HORIZONTAL = "rectangle-horizontal"
    RECTANGLE_VERTICAL = "rectangle-vertical"