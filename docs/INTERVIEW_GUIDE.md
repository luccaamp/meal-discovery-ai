# Explicar o projeto com autoria e evidências

A implementação foi assistida por IA. Antes de apresentar domínio de uma ferramenta, o autor deve executar, revisar e explicar sua parte. Não transformar código gerado em alegação de experiência que ainda não consegue demonstrar.

1. **Dados reais:** mostrar a cadeia ZIP → SHA-256 → preparação → manifesto → SQLite. Explicar os 35 pedidos em quarentena e por que excluir somente o item quebrado mudaria a cesta.
2. **Vazamento temporal:** identificar treino até o dia 61, validação interna 62–75 e teste oficial separado 76–90. Mostrar o teste automatizado que impede influência de pedidos futuros.
3. **Referências:** explicar por que repetição pessoal superou o modelo por cestas e por que isso não prova aumento de vendas. Interpretar Recall e NDCG com um exemplo pequeno.
4. **Recomendação de produto:** mostrar que o usuário seleciona referências reais, sem histórico inventado. Explicar cosseno, shrinkage, top-100 vizinhos e fallback. A soma de coocorrências por sementes não representa necessariamente cestas únicas.
5. **Embeddings:** explicar consulta/documento, pooling, máscara, normalização e produto escalar. Apresentar o resultado negativo de português e as limitações dos rótulos automáticos.
6. **LLM e ferramentas:** localizar o prompt, o schema de intenção e a allowlist. Mostrar uma chamada real, seu consumo de tokens e a origem de um item. Distinguir planejamento por LLM de resposta factual montada pelo domínio.
7. **Confiabilidade:** simular modelo indisponível, lista vazia, filtro inválido e restrição alimentar. Explicar por que um nome não comprova ingrediente nem ausência de alérgeno.
8. **Produto:** demonstrar busca, diálogo de evidências, seleção, conversa e laboratório em desktop/celular. Identificar o que ainda precisa de estudo com pessoas.
9. **n8n:** importar o workflow, executá-lo, conferir os três nós e o Markdown gerado. Explicar versionamento e por que métricas de protocolos diferentes não são comparadas como regressão.
10. **Limites honestos:** não houve fine-tuning próprio, publicação de modelo na conta do autor, execução comercial GPT/Claude/Gemini, teste oficial ou implantação pública. Explicar o próximo experimento e seus critérios antes de escolher mais ferramentas.

Sugestão de apresentação: dois minutos para produto, dois para método e resultados, um para uma falha concreta e um para o próximo passo. Preservar os resultados negativos: eles mostram análise quando acompanhados de diagnóstico e decisão verificável.
