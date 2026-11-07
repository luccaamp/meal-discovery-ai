# Estado do projeto e produto final

## Entregue e executado

- Fontes oficiais de três cidades verificadas; Singapura como base principal, com manifesto, quarentena e teste oficial separado.
- Três referências de recomendação avaliadas em 175.358 clientes de validação interna. Repetição pessoal foi a melhor medida, sem afirmar impacto comercial.
- Catálogo lexical com 1.066.840 produtos reais, filtros, API somente leitura, OpenAPI e validação por HTTP.
- Piloto local de embeddings e busca híbrida em 10.000 produtos reais, com revisão/SHA do modelo fixados e comparação de desenvolvimento publicada.
- Testes automatizados, CI, instruções de reprodução e distinção explícita entre dados reais e fixtures de teste.

O piloto semântico ainda não atende o critério de qualidade para substituir a busca da API. Sua avaliação usa rótulos automáticos incompletos; a revisão humana foi preparada e não foi realizada. [Experimento 003](EXPERIMENT_003.md).

## Falta para concluir

1. Relevância: revisão humana, consultas adicionais e avaliação reservada; comparar alternativas multilíngues e validar a expansão do índice.
2. Assistente: LLM com ferramentas de busca/recomendação/detalhe, esclarecimento de preferências e evidência ligada a IDs existentes. Comparar modelos/provedores conforme acesso e orçamento.
3. Avaliação generativa: fidelidade ao catálogo, argumentos de ferramentas, restrições, erros, custo e latência; não confundir associação com garantia alimentar.
4. Produto: frontend profissional e responsivo, conversa e resultados sincronizados, filtros, evidências, estados de erro e acessibilidade.
5. Operação: rastreabilidade das chamadas de IA, limites e automação n8n executada e medida; implantação da demonstração.
6. Portfólio: demonstração gravada, explicação da arquitetura, relatório dos resultados e roteiro de estudo para o autor defender decisões na entrevista.

Hugging Face já foi usado para obter e verificar um modelo pré-treinado. GPT/Claude/Gemini, orquestração de agente e n8n ainda não têm execução demonstrada neste projeto. Uso de uma ferramenta não comprova uso de outras; fine-tuning e um servidor MCP próprio permanecem extensões condicionadas a necessidade real.

## Experiência final pretendida

A aplicação terá identidade visual própria, com exploração de refeições reais, consulta em português, refinamento por conversa e recomendações com evidências. A pessoa poderá conferir nome original, culinária, preço normalizado, versão e origem dos atributos de cada resultado. Restrições não comprovadas pelos dados exigirão esclarecimento.

Um laboratório mostrará comparações de recomendação e recuperação, qualidade do assistente, cobertura, custo, latência e erros observados. O repositório reunirá código, contratos, modelos/protocolos versionados, automações e reprodução dos experimentos.

O catálogo é histórico: o produto não promete estoque, compra, entrega atual ou preço em reais. O objetivo é demonstrar engenharia de IA, análise e produto com evidências que o candidato saiba explicar; não existe garantia de aprovação na seleção.
