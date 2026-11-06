# Arquitetura proposta

Implementados: auditor CSV, mapeamento explícito, importação relacional em SQLite e benchmark de três recomendadores. A cópia real derivada do DHRD foi baixada e auditada; falta adaptar seu formato para treinamento. Fixtures sintéticas existem somente em testes. API, índices de busca, agente, frontend e n8n permanecem planejados.

Fluxo executável atual: CSVs com mapeamento explícito → contratos e hashes → SQLite somente leitura para análise → perfis de treino congelados → popularidade/repetição/cosseno → relatório de avaliação. SQLite foi escolhido para integridade e transações sem dependência de execução adicional; a arquitetura abaixo permanece a visão de evolução.

```mermaid
flowchart LR
  D[DHRD obtido da fonte] --> A[Auditoria e contratos]
  A --> P[Parquet e DuckDB]
  P --> T[Treino e avaliação temporal]
  P --> S[Índices lexical e semântico]
  T --> R[Recomendador versionado]
  S --> F[Funções de domínio]
  R --> F
  F --> API[FastAPI]
  F --> AG[Agente com ferramentas]
  AG --> API
  API --> UI[React e TypeScript]
  T --> E[Artefatos de avaliação]
  AG --> E
  E --> N[n8n: validação e relatório]
  F -. extensão .-> MCP[Adaptador MCP]
```

Python para dados e modelos; DuckDB/Parquet são opções futuras de processamento; FastAPI para contratos; React/TypeScript e tokens CSS para interface. Versões de dependências e arquivo de lock serão fixados ao implementar cada componente e verificar compatibilidade. Não incluir dependências vazias apenas para aparência de completude.

Contratos candidatos: `search_catalog(query, filters, limit)`, `recommend(profile_id, filters, limit)`, `get_item(item_id)`, `get_evaluation(run_id)`. Saídas terão IDs, metadados, origem, versão e avisos de cobertura. Nunca aceitar SQL, código arbitrário ou URLs fornecidas pelo LLM para execução.

Separar os modelos de recuperação/ranking do modelo de linguagem. A interface consulta o mesmo serviço usado pelo agente, permitindo comparar filtros convencionais com conversa. Pontuação de ranking não será apresentada como probabilidade de satisfação.

Registrar run_id, versões, ferramenta, duração, tokens/custo quando disponíveis e erros. Remover credenciais e limitar persistência do conteúdo de conversa. Incluir modo sem LLM para falhas ou orçamento esgotado. Resultados sintéticos de desenvolvimento serão identificados e separados dos resultados com DHRD.
