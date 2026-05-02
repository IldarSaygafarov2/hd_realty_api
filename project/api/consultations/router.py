from ninja import Router

from project.apps.consultations.models import (
    ConsultationRequest,
    ContactRequest,
    NextStepRequest,
)
from project.apps.consultations.schemas import (
    ConsultationRequestCreateSchema,
    ConsultationRequestSchema,
    ContactRequestCreateSchema,
    ContactRequestSchema,
    NextStepRequestCreateSchema,
    NextStepRequestSchema,
)

router = Router(tags=["consultations"])


def _to_consultation_schema(obj: ConsultationRequest) -> ConsultationRequestSchema:
    return ConsultationRequestSchema(
        id=obj.id,
        name=obj.name,
        phone=obj.phone,
        goal=obj.goal,
        status=obj.status,
        created_at=obj.created_at.isoformat() if obj.created_at else "",
    )


def _to_contact_schema(obj: ContactRequest) -> ContactRequestSchema:
    return ContactRequestSchema(
        id=obj.id,
        name=obj.name,
        phone=obj.phone,
        status=obj.status,
        created_at=obj.created_at.isoformat() if obj.created_at else "",
    )


@router.post("/consultations", response={201: ConsultationRequestSchema})
def create_consultation_request(request, payload: ConsultationRequestCreateSchema):
    """Принять заявку с формы «Получите экспертную оценку»."""
    obj = ConsultationRequest.objects.create(
        name=payload.name.strip(),
        phone=payload.phone.strip(),
        goal=payload.goal,
    )
    return 201, _to_consultation_schema(obj)


@router.post("/contact-requests", response={201: ContactRequestSchema})
def create_contact_request(request, payload: ContactRequestCreateSchema):
    """Принять заявку с формы «Оставьте заявку — подскажем следующий шаг»."""
    obj = ContactRequest.objects.create(
        name=payload.name.strip(),
        phone=payload.phone.strip(),
    )
    return 201, _to_contact_schema(obj)


def _to_next_step_schema(obj: NextStepRequest) -> NextStepRequestSchema:
    return NextStepRequestSchema(
        id=obj.id,
        name=obj.name,
        phone=obj.phone,
        task_description=obj.task_description or "",
        status=obj.status,
        created_at=obj.created_at.isoformat() if obj.created_at else "",
    )


@router.post("/next-step-requests", response={201: NextStepRequestSchema})
def create_next_step_request(request, payload: NextStepRequestCreateSchema):
    """Принять заявку с формы «Оставьте заявку — подскажем следующий шаг»."""
    obj = NextStepRequest.objects.create(
        name=payload.name.strip(),
        phone=payload.phone.strip(),
        task_description=(payload.task_description or "").strip(),
    )
    return 201, _to_next_step_schema(obj)
