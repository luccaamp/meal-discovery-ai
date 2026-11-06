# Registro de decisões

## 2026-11-06 — Escolha e fundação

- Hipótese: recomendação com busca conversacional permite evidenciar ML, LLMs e produto de forma integrada.
- Decisão: projeto 5B escolhido pelo usuário; foco em uma cidade e uma tarefa principal.
- Melhoria: explicitar avaliação, uso das ferramentas citadas na vaga, autoria e direção visual; adiar previsão de demanda.
- Implementação inicial: estrutura do repositório, auditor CSV sem dependências de execução, testes e configuração de CI.
- Resultado de dados/modelos: nenhum experimento DHRD realizado.
- Limitação: acesso aos arquivos ainda pendente; prazos de desenvolvimento são estimativas.
- Próxima decisão: obter os arquivos oficiais e escolher cidade e cortes a partir da auditoria.

Template dos próximos registros: hipótese → alteração → comparação → resultado observado → limitação → próxima decisão. Informar assistência de IA e revisão humana relevante.

## 2026-11-06 — Importação relacional e referências de recomendação

- Hipótese: um contrato explícito e um benchmark simples permitem iniciar a engenharia enquanto a aquisição dos arquivos é resolvida.
- Implementação: CSVs configuráveis → SQLite transacional → treino congelado por dia relativo → primeira cesta futura por cliente. Itens identificados pelo par vendedor/produto, com referências de popularidade, repetição e cosseno colaborativo.
- Comparação: testes incluem resultado calculado à mão, cliente novo, alvo fora do catálogo, dados órfãos e duplicatas conflitantes. Adicionar eventos após o período de avaliação não alterou Recall/NDCG da validação no teste de regressão.
- Resultado observado: 19 testes automatizados passaram localmente e a demonstração sintética executou de ponta a ponta. Nenhuma conclusão sobre qualidade ou escala em dados reais.
- Limitação: link oficial sem autenticação redireciona para login. Formato real e protocolo dos splits distribuídos permanecem desconhecidos. O benchmark inicial não aplica restrição geográfica nem disponibilidade.
- Decisão: não escolher cidade, inventar métricas ou trocar a base. SQLite usa biblioteca padrão e garante integridade nesta etapa; DuckDB/Parquet serão reconsiderados a partir dos arquivos e medições.
- Próxima ação: obter distribuição oficial acessível e validar o adaptador. Funções de catálogo e API poderão avançar em paralelo com os contratos conhecidos.
- Assistência: implementação e documentação produzidas com Codex; compreensão e revisão pelo candidato ainda precisam ser verificadas.
