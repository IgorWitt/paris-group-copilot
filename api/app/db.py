"""Conexão com o PostgreSQL (via Docker Compose) e modelos das entidades do Copilot."""
import os

from sqlalchemy import ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://copilot:copilot@localhost:5432/copilot"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Projeto(Base):
    """Um MVP do venture studio: o que Marina está descobrindo agora."""

    __tablename__ = "projetos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    contexto: Mapped[str] = mapped_column(Text, default="")
    dor_do_usuario: Mapped[str] = mapped_column(Text, default="")


class Hipotese(Base):
    """Uma aposta de valor ligada a um projeto, no formato se/então/porque, com métrica."""

    __tablename__ = "hipoteses"

    id: Mapped[int] = mapped_column(primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.id", ondelete="CASCADE"))
    se: Mapped[str] = mapped_column(Text)
    entao: Mapped[str] = mapped_column(Text)
    porque: Mapped[str] = mapped_column(Text)
    metrica: Mapped[str] = mapped_column(Text)
    resultado: Mapped[str] = mapped_column(String(20), default="aberta")  # aberta | confirmada | refutada


def init_db() -> None:
    Base.metadata.create_all(engine)
