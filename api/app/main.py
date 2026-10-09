"""Paris Group Copilot — API (FastAPI).

Duas entidades do enquadramento (docs/enquadramento.md): Projeto e Hipótese.
O contrato OpenAPI é gerado pelo FastAPI e fica em /docs.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Hipotese, Projeto, SessionLocal, init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Paris Group Copilot API",
    version="0.1.0",
    description="Registra projetos (MVPs) e as hipóteses de valor testadas em cada um, "
    "para que o aprendizado de um MVP não se perca no próximo.",
    lifespan=lifespan,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Schemas (contrato) ----------
class ProjetoIn(BaseModel):
    nome: str = Field(..., examples=["Movia"])
    contexto: str = Field("", examples=["Revendas de seminovos em Chapecó"])
    dor_do_usuario: str = Field("", examples=["Lead do anúncio fica horas sem resposta"])


class ProjetoOut(ProjetoIn):
    id: int


class HipoteseIn(BaseModel):
    projeto_id: int
    se: str = Field(..., examples=["o sistema responder o lead em menos de 2 minutos"])
    entao: str = Field(..., examples=["a loja vende mais carros do anúncio"])
    porque: str = Field(..., examples=["o comprador fecha com quem responde primeiro"])
    metrica: str = Field(..., examples=["carros vendidos por lead de anúncio, por mês"])


class HipoteseOut(HipoteseIn):
    id: int
    resultado: str


class ResultadoIn(BaseModel):
    resultado: str = Field(..., pattern="^(aberta|confirmada|refutada)$")


# ---------- Endpoints ----------
@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}


@app.post("/projetos", response_model=ProjetoOut, status_code=201, tags=["projetos"])
def criar_projeto(body: ProjetoIn, db: Session = Depends(get_db)):
    p = Projeto(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/projetos", response_model=list[ProjetoOut], tags=["projetos"])
def listar_projetos(db: Session = Depends(get_db)):
    return db.scalars(select(Projeto).order_by(Projeto.id)).all()


@app.get("/projetos/{projeto_id}", response_model=ProjetoOut, tags=["projetos"])
def obter_projeto(projeto_id: int, db: Session = Depends(get_db)):
    p = db.get(Projeto, projeto_id)
    if not p:
        raise HTTPException(404, "Projeto não encontrado")
    return p


@app.post("/hipoteses", response_model=HipoteseOut, status_code=201, tags=["hipoteses"])
def criar_hipotese(body: HipoteseIn, db: Session = Depends(get_db)):
    if not db.get(Projeto, body.projeto_id):
        raise HTTPException(404, "Projeto não encontrado")
    h = Hipotese(**body.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@app.get("/hipoteses", response_model=list[HipoteseOut], tags=["hipoteses"])
def listar_hipoteses(projeto_id: int | None = None, db: Session = Depends(get_db)):
    q = select(Hipotese).order_by(Hipotese.id)
    if projeto_id is not None:
        q = q.where(Hipotese.projeto_id == projeto_id)
    return db.scalars(q).all()


@app.patch("/hipoteses/{hipotese_id}/resultado", response_model=HipoteseOut, tags=["hipoteses"])
def registrar_resultado(hipotese_id: int, body: ResultadoIn, db: Session = Depends(get_db)):
    """É aqui que o aprendizado fica guardado: confirmada ou refutada, para o próximo MVP consultar."""
    h = db.get(Hipotese, hipotese_id)
    if not h:
        raise HTTPException(404, "Hipótese não encontrada")
    h.resultado = body.resultado
    db.commit()
    db.refresh(h)
    return h
