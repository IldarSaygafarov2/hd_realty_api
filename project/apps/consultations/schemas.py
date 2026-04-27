from ninja import Schema
from pydantic import Field


class ConsultationRequestCreateSchema(Schema):
    """Входящие данные с формы «Получите экспертную оценку»."""

    name: str = Field(..., min_length=1, max_length=150)
    phone: str = Field(..., min_length=3, max_length=32)
    goal: str = Field(..., pattern=r"^(buy|sell)$")


class ConsultationRequestSchema(Schema):
    """Заявка на консультацию (ответ API)."""

    id: int
    name: str
    phone: str
    goal: str
    status: str
    created_at: str


class ContactRequestCreateSchema(Schema):
    """Входящие данные с формы «Оставьте заявку — подскажем следующий шаг»."""

    name: str = Field(..., min_length=1, max_length=150)
    phone: str = Field(..., min_length=3, max_length=32)


class ContactRequestSchema(Schema):
    """Заявка на обратный звонок (ответ API)."""

    id: int
    name: str
    phone: str
    status: str
    created_at: str
