from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from config.database import Base


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(
        Enum("tarefas_diarias", "tarefas_educacionais", name="tipo_tarefa_enum"),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prioridade: Mapped[str] = mapped_column(
        Enum("baixa", "media", "alta", name="prioridade_enum"),
        nullable=False,
        default="media",
    )
    prazo: Mapped[Optional[date]] = mapped_column(nullable=True)
    concluida: Mapped[bool] = mapped_column(nullable=False, default=False)
    criado_em: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="tarefas")

    # passive_deletes: quem apaga os passos é o ON DELETE CASCADE do banco.
    passos: Mapped[List["Passo"]] = relationship(
        back_populates="tarefa",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Passo.ordem",
    )
