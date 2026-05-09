from pydantic import BaseModel, Field, field_validator

ALLOWED_THEME_MODES = {"system", "light", "dark"}
ALLOWED_ACCENT_COLORS = {"blue", "green", "teal", "indigo", "slate"}


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=80)
    last_name: str | None = Field(default=None, max_length=80)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    city: str | None = Field(default=None, max_length=100)
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)
    payday: int | None = Field(default=None, ge=1, le=31)
    income_frequency: str | None = Field(
        default=None, pattern="^(monthly|biweekly|weekly|variable)$"
    )

    @field_validator("first_name", "last_name", "city", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return " ".join(value.strip().split())

    @field_validator("country_code", "currency_code", mode="after")
    @classmethod
    def uppercase_codes(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class SettingsUpdate(BaseModel):
    theme_mode: str | None = None
    accent_color: str | None = None
    dashboard_layout: dict | None = None
    notification_settings: dict | None = None

    @field_validator("theme_mode")
    @classmethod
    def validate_theme(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_THEME_MODES:
            raise ValueError("Tema no permitido.")
        return value

    @field_validator("accent_color")
    @classmethod
    def validate_accent(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_ACCENT_COLORS:
            raise ValueError("Color no permitido.")
        return value
