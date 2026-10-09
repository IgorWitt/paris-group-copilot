# Arquitetura — Paris Group Copilot

Este documento justifica cada peça da stack pelos dois critérios do modelo de Venture Studio: **velocidade de criar um MVP** e **reutilização entre os produtos do studio**, sem esquecer a **manutenção simples**, porque o time que mantém 5 MVPs é o mesmo que criou o primeiro.

O contrato do produto está em [enquadramento.md](enquadramento.md). Tudo aqui existe para servir àquela hipótese: guardar o que cada MVP aprendeu (Projeto → Hipóteses → resultado) e devolver isso na próxima sessão de discovery.

## Visão geral

| Camada | Escolha | Onde está |
|---|---|---|
| Interface | Next.js 15 (App Router, TypeScript, Tailwind) | `src/app` |
| API | FastAPI (Python 3.12) | `api/app` |
| Dados | PostgreSQL 16 | `docker-compose.yml` (serviço `db`) |
| Contrato | OpenAPI gerado pelo FastAPI | `http://localhost:8000/docs` |
| Infra local | Docker Compose (api + db) | raiz do repositório |

Monorepo: interface e API no mesmo repositório. Um MVP novo do studio nasce clonando esta estrutura inteira, não juntando peças de três repositórios.

## Por que Next.js, e não Remix ou Vite + React

- **Velocidade de MVP:** `create-next-app` entrega roteamento, build, TypeScript, Tailwind e ESLint prontos em um comando. As páginas `/projeto` e `/hipotese` existiram em minutos. Remix exige mais decisões de loader/action antes da primeira tela aparecer; Vite + React exige montar roteamento e SSR à mão.
- **Reutilização:** o App Router dá uma convenção de pastas (`src/app/<rota>/page.tsx`) que qualquer pessoa do studio reconhece ao abrir o próximo MVP. Padrão de pasta é o que permite copiar um MVP e trocar só o domínio.
- **Manutenção:** é o framework com maior base de exemplos e de deploy sem configuração (Vercel, Railway). Quando o time é pequeno, o custo de "como se faz X" é o que mais atrasa.

## Por que FastAPI, e não Express

- **Velocidade de MVP:** o contrato OpenAPI sai de graça dos tipos Pydantic. Os schemas `ProjetoIn`, `HipoteseIn` e `ResultadoIn` viraram `/docs` sem escrever documentação. Em Express, o contrato é um artefato separado que envelhece.
- **Reutilização:** os produtos do studio usam IA (resumo de hipóteses, sugestão de enquadramento). O ecossistema de IA é Python: a mesma API que guarda dados é a que vai chamar o modelo, sem uma segunda linguagem no backend.
- **Manutenção:** validação de entrada no tipo, não em `if`s espalhados. Uma hipótese sem `metrica` é recusada na borda, com erro legível, antes de chegar ao banco.

## Por que PostgreSQL, e não SQLite

- **Velocidade de MVP:** o SQLite seria mais rápido para começar, e essa é a tentação. Mas o Copilot só tem valor se **vários** projetos e pessoas gravarem hipóteses ao mesmo tempo (Marina e os stakeholders na mesma sessão). SQLite serializa escritas; o produto nasceria com um limite que o enquadramento já contradiz.
- **Reutilização:** o PostgreSQL é o mesmo banco dos outros produtos do grupo (Movia, Vordin). Conhecimento de operação, backup e consulta se repete entre os MVPs. Trocar de banco por MVP é retrabalho puro.
- **Manutenção:** o esquema vive no código (`api/app/db.py`, SQLAlchemy 2) e o banco sobe com um `docker compose up`. Ninguém instala Postgres na máquina nem configura usuário à mão.

## Por que Docker Compose

Dois serviços (`api`, `db`) com um comando. O `healthcheck` do banco garante que a API só sobe quando o Postgres aceita conexão; sem isso, o primeiro `up` de todo MVP novo falhava "às vezes". O próximo produto do studio copia o `docker-compose.yml` e troca o nome do banco.

## O que fica fora, de propósito

- Sem autenticação no MVP: o produto roda dentro do studio, com uma equipe. Entra quando houver cliente externo.
- Sem fila ou cache: o volume é de dezenas de hipóteses por projeto, não de milhares de eventos por segundo.
- Sem migrações versionadas (Alembic) enquanto o esquema tiver duas tabelas; entra na primeira mudança incompatível.

## Como rodar

```bash
docker compose up --build        # sobe db + api
open http://localhost:8000/docs  # contrato OpenAPI
npm run dev                      # interface em http://localhost:3000
```
