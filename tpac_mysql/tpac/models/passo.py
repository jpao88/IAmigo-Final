from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class Passo(Base):
    __tablename__ = "passos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tarefa_id: Mapped[int] = mapped_column(
        ForeignKey("tarefas.id", ondelete="CASCADE"), nullable=False
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    concluido: Mapped[bool] = mapped_column(nullable=False, default=False)
    ordem: Mapped[int] = mapped_column(nullable=False, default=1)

    tarefa: Mapped["Tarefa"] = relationship(back_populates="passos")
