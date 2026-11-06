# Protocolo de avaliação

Status: protocolo proposto. Não há resultados.

## Recomendação e recuperação

Auditar os splits fornecidos antes de utilizá-los. Reservar teste sem ajuste de hiperparâmetros; validação deriva apenas do treino, respeitando tempo. Itens do mesmo pedido não podem atravessar partições. Garantir que perfis, popularidade e embeddings treináveis não consumam interações futuras; documentar que um catálogo final pode conter itens ainda inexistentes no corte histórico.

Definir unidade, catálogo candidato, exclusões, disponibilidade aproximada por região e política de repetição. Compras repetidas são relevantes em refeições: comparar política que permite repetição com análise específica de novidade. Ausência de compra não comprova rejeição; negativos amostrados e catálogo completo geram métricas diferentes.

Referências: popularidade global/local e repetição do histórico. Candidatos: filtragem colaborativa implícita, busca lexical, embeddings e combinação de sinais. Escolher algoritmo e biblioteca após auditoria, escala e benchmark inicial.

Medir Recall@10, NDCG@10, cobertura do catálogo, diversidade e latência p50/p95, com protocolo e tamanho das amostras. Separar perfis novos e pouco ativos, itens novos e regiões. Para busca, criar consultas com julgamentos humanos de relevância, incluindo consultas em português sobre catálogo multilíngue. Informar variabilidade por usuário/período; não comparar números de protocolos distintos.

## LLM e fluxo completo

Alvo inicial: 60 casos julgados, 40 de desenvolvimento e 20 de teste congelado. O arquivo de exemplos é somente desenvolvimento, não um conjunto reservado. Cobrir busca direta, preferências múltiplas, continuação, ausência de resultados, ambiguidade, limites de preço, conteúdo malicioso no catálogo e atributos desconhecidos.

Medir: ferramenta correta, argumentos válidos, IDs existentes, cumprimento dos filtros, números e evidências corretos, esclarecimentos e afirmações sem suporte. Julgar uma amostra manualmente mesmo que exista avaliador por LLM. Comparar prompt simples, fluxo com ferramentas e variantes; manter o teste fora de ajustes.

Registrar provedor/modelo/versão, parâmetros, número de chamadas, falhas, tempo e custo baseado em uso/preço verificados na data do experimento. Comparar mesma tarefa via interface convencional. Não confundir sucesso da chamada HTTP com sucesso da tarefa.

## Automação e usuários

Cronometrar a mesma tarefa manual e automatizada de consolidação de relatório; registrar quantidade de execuções, supervisão e correções. Não extrapolar economia anual sem observar frequência. Em teste de uso, medir conclusão, tempo e obstáculos; não inferir conversão comercial a partir de opinião ou cliques da demo.
