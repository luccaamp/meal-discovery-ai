# Meal Discovery AI

Recomendação de refeições e busca conversacional com dados reais da Delivery Hero.

**Status: distribuição oficial completa obtida e auditada.** Os três ZIPs contêm quinze arquivos de Singapura, Estocolmo e Taipei, somando 4.400.000 pedidos. Singapura será a fonte principal. Os campos usados no primeiro experimento coincidem linha a linha com os originais; seus resultados históricos permanecem identificados como execução sobre o espelho. Nenhuma métrica foi calculada nos testes oficiais. Interface e LLM permanecem planejados.

[Quais arquivos usar, comparação e plano de migração](docs/OFFICIAL_DATA_MIGRATION.md).

| Referência | Recall@10 | NDCG@10 |
| --- | ---: | ---: |
| Popularidade global | 0,2504% | 0,001166 |
| Repetição pessoal | **16,0427%** | **0,127100** |
| Similaridade por cesta | 6,7272% | 0,042941 |

Métricas offline sobre a primeira cesta futura de cada cliente. Sem filtro geográfico e sem comprovação de impacto comercial. [Experimento, protocolo e limitações](docs/EXPERIMENT_001.md).

## Produto proposto

Explorar um catálogo histórico, receber recomendações e refinar preferências por conversa, com explicações ligadas às evidências disponíveis. Um laboratório apresenta comparações de modelos, qualidade do assistente, custo e latência. Projeto independente, sem vínculo com Delivery Hero ou iFood.

## Começar

Python 3.11 ou superior. O auditor inicial usa somente a biblioteca padrão.

```sh
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
python -m meal_discovery --help
python -m unittest discover -s tests -v
```

Com os ZIPs oficiais na raiz do projeto:

```sh
python scripts/verify_official_archives.py
python scripts/audit_official_data.py
```

O primeiro comando confere os hashes e extrai os quinze CSVs `.txt` para `data/raw/dhrd-official-v1/`. O segundo audita os três splits e compara Singapura com a cópia histórica local. O relatório oficial já executado está versionado em `evaluations/results/`. Não usa o teste para medir ou ajustar modelos. [Fontes e papéis](configs/official-source-selection-v1.json).

Para reproduzir a aquisição e o Experimento 001 históricos:

```sh
python scripts/fetch_hyperhawkes.py
python scripts/fetch_nearbite_sg.py
python scripts/audit_nearbite_sg.py
python -m meal_discovery prepare-singapore --output data/processed/singapore-v1.sqlite
python -m meal_discovery validate-singapore --database data/processed/singapore-v1.sqlite --output reports/singapore-validation-v1.json
```

O primeiro downloader fixa revisão e hash Git do derivado HyperHawkes. O segundo obtém as três tabelas públicas de Singapura (419.360.922 bytes), confere tamanho/cabeçalho e registra SHA-256. Os arquivos ficam em `data/raw/`, ignorado pelo Git. O auditor examina todas as linhas e relações, sem publicar registros individuais. Escolha outro `--output` para repetir uma auditoria já salva.

A cópia de Singapura tem pedidos dos dias relativos 0–75 e inclui preço normalizado, categoria de culinária e geohash; coordenadas adicionais foram derivadas do geohash pelo autor do espelho. As 41 linhas de itens sem cadastro levaram à quarentena dos 35 pedidos afetados por inteiro. Fontes brutas permanecem intactas. Não afirmar equivalência byte a byte ao pacote original. Ver [procedência e limites](docs/DATA_ACCESS.md) e [busca pela distribuição completa](docs/SOURCE_SEARCH_2026-11-06.md).

O protocolo versionado usa treino nos dias 0–61, validação nos dias 62–68 e reserva 69–75 para teste. Os comandos protegem saídas existentes; para repetir, escolha novos nomes de banco e relatório.

**Política de dados reais:** comandos públicos de preparação e benchmark rejeitam fontes marcadas como sintéticas. O comando `demo` foi removido. Pequenas fixtures inventadas ficam exclusivamente em `tests/`; não há fallback sintético no produto.

```sh
python -m meal_discovery audit --input-dir data/raw --output reports/data-audit.json
```

O comando registra hashes, cabeçalhos, linhas, células vazias e larguras inconsistentes, sem exportar valores das linhas. Use `--delimiter` e `--encoding` se necessário. Não substitui auditoria relacional ou temporal. Nenhum CSV encontrado resulta em erro explícito, sem relatório de sucesso vazio.

A preparação relacional usa um mapeamento explícito de colunas, preserva produtos por estabelecimento e rejeita pedidos inconsistentes ou referências ausentes. O benchmark compara popularidade, repetição e similaridade colaborativa, com Recall@K, NDCG@K e análise de clientes novos. Consulte [comandos, contratos e limites](docs/DATA_PIPELINE.md) antes de configurar uma base real. Relatórios e bancos existentes não são sobrescritos.

## Estrutura

```text
apps/api/           API de produto (planejada)
apps/web/           interface React/TypeScript (planejada)
src/meal_discovery/ auditoria, importação, recomendação e avaliação
configs/           exemplo de mapeamento explícito de CSVs
data/              obtenção e armazenamento local, ignorado no Git
models/            documentação de artefatos futuros
evaluations/       protocolo e exemplos de casos de desenvolvimento
prompts/           contratos e versões futuras de prompts
workflows/n8n/     automação planejada e critérios de validação
docs/              plano, arquitetura, design e evidências
reports/           relatórios locais, ignorados no Git
tests/             verificações de integridade do auditor
```

## Documentação

- [Plano e marcos](docs/PROJECT_PLAN.md)
- [Primeiro experimento real e análise de erros](docs/EXPERIMENT_001.md)
- [Ferramentas e evidências para o portfólio](docs/SKILLS_EVIDENCE.md)
- [Arquitetura e decisões](docs/ARCHITECTURE.md)
- [Experiência e direção visual](docs/DESIGN.md)
- [Protocolo de avaliação](evaluations/README.md)
- [Dados, procedência e limitações](data/README.md)
- [Pipeline e benchmark executáveis](docs/DATA_PIPELINE.md)
- [Explicação da implementação para estudo](docs/LEARNING.md)
- [Registro de decisões](docs/DECISIONS.md)

As funcionalidades serão marcadas como entregues apenas com execução e evidência. Este repositório está em desenvolvimento; busca, API, LLM e produto visual permanecem como próximos marcos.

## Fontes

[DHRD e instruções de acesso](https://github.com/deliveryhero/dh-reco-dataset) · [Artigo RecSys 2023](https://doi.org/10.1145/3604915.3610242)

Código sob MIT; dados e modelos de terceiros mantêm seus próprios termos. Nenhum dataset acompanha este repositório.
