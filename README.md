# Meal Discovery AI

Recomendação de refeições e busca conversacional com dados reais da Delivery Hero.

**Status: pipeline e referências de recomendação implementados.** Auditoria CSV, importação relacional em SQLite e avaliação temporal executam localmente. Há três recomendadores de referência e uma demonstração sintética. Os arquivos DHRD ainda não foram obtidos; não há métricas reais, interface ou integração com LLM nesta versão.

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
python -m meal_discovery demo --output-dir reports/synthetic-demo-v1
```

O último comando usa pequenos exemplos inventados para conferir o funcionamento e identifica explicitamente `data_kind: synthetic`. Ele não mede a qualidade do projeto nos dados da Delivery Hero.

Para dados reais, obtenha os arquivos pela [fonte oficial](https://github.com/deliveryhero/dh-reco-dataset), confira os termos e inspecione o formato. O link oficial está redirecionando para login nesta verificação; [situação de acesso](docs/DATA_ACCESS.md). Arquivos compactados/Parquet ainda não são lidos.

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
- [Ferramentas e evidências para o portfólio](docs/SKILLS_EVIDENCE.md)
- [Arquitetura e decisões](docs/ARCHITECTURE.md)
- [Experiência e direção visual](docs/DESIGN.md)
- [Protocolo de avaliação](evaluations/README.md)
- [Dados, procedência e limitações](data/README.md)
- [Pipeline e benchmark executáveis](docs/DATA_PIPELINE.md)
- [Explicação da implementação para estudo](docs/LEARNING.md)
- [Registro de decisões](docs/DECISIONS.md)

As funcionalidades serão marcadas como entregues apenas com execução e evidência. Este repositório está em desenvolvimento; dados reais, LLM e produto visual permanecem como próximos marcos.

## Fontes

[DHRD e instruções de acesso](https://github.com/deliveryhero/dh-reco-dataset) · [Artigo RecSys 2023](https://doi.org/10.1145/3604915.3610242)

Código sob MIT; dados e modelos de terceiros mantêm seus próprios termos. Nenhum dataset acompanha este repositório.
