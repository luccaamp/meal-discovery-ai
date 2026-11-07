# Estado do projeto e produto final

## Entregue e executado

- Interface Mesa em React/TypeScript: exploração, evidências, seleção de itens, conversa e laboratório, conectados à API real. Layouts 360/768/1440 CSS verificados.
- Qwen2.5-1.5B local com planejamento estruturado e ferramentas controladas; refinamento explícito de filtros e esclarecimento de restrições não comprovadas.
- Artefato persistido de popularidade/vizinhos por cestas, ajustado até o dia 61 e servido com procedência.
- 13/13 contratos HTTP reais do assistente, com 48 itens conferidos contra o catálogo, tokens e latências registrados.
- Workflow n8n executado: três nós, dois experimentos e relatório Markdown sanitizado. Sem envio de mensagens a terceiros.

- Fontes oficiais de três cidades verificadas; Singapura como base principal, com manifesto, quarentena e teste oficial separado.
- Três referências de recomendação avaliadas em 175.358 clientes de validação interna. Repetição pessoal foi a melhor medida, sem afirmar impacto comercial.
- Catálogo lexical com 1.066.840 produtos reais, filtros, API somente leitura, OpenAPI e validação por HTTP.
- Piloto local de embeddings e busca híbrida em 10.000 produtos reais, com revisão/SHA do modelo fixados e comparação de desenvolvimento publicada.
- Testes automatizados, CI, instruções de reprodução e distinção explícita entre dados reais e fixtures de teste.

O piloto semântico ainda não atende o critério de qualidade para substituir a busca da API. Sua avaliação usa rótulos automáticos incompletos; a revisão humana foi preparada e não foi realizada. [Experimento 003](EXPERIMENT_003.md).

## Falta para concluir

O produto local está executável pelo [guia completo](PRODUCT_GUIDE.md). O trabalho restante exige avaliação independente, participação humana ou infraestrutura de publicação.

1. Relevância: revisão humana, consultas adicionais e avaliação reservada; comparar alternativas multilíngues e validar a expansão do índice.
2. Assistente: comparar outro modelo/provedor e ampliar os casos reservados, sem chamar os contratos de desenvolvimento de prova de generalização.
3. Uso: testar tarefas com pessoas e revisar acessibilidade de forma mais ampla, além dos contratos e inspeção já executados.
4. Operação: escolher hospedagem, configurar proteção/limites e publicar o backend, modelo e interface. Agendamento e alertas no n8n continuam opcionais; não medir economia sem referência manual.
5. Portfólio: o autor revisar o código, executar o roteiro e gravar sua demonstração. Guia de estudo já entregue em INTERVIEW_GUIDE.md.

Hugging Face já forneceu modelos pré-treinados verificados e executados. O planejador local e n8n têm execução demonstrada; GPT/Claude/Gemini não. Existe adaptador opcional OpenAI sem execução comercial. Uso de uma ferramenta não comprova uso de outras; fine-tuning e MCP próprio permanecem extensões condicionadas a necessidade real.

## Experiência final pretendida

A aplicação terá identidade visual própria, com exploração de refeições reais, consulta em português, refinamento por conversa e recomendações com evidências. A pessoa poderá conferir nome original, culinária, preço normalizado, versão e origem dos atributos de cada resultado. Restrições não comprovadas pelos dados exigirão esclarecimento.

Um laboratório mostrará comparações de recomendação e recuperação, qualidade do assistente, cobertura, custo, latência e erros observados. O repositório reunirá código, contratos, modelos/protocolos versionados, automações e reprodução dos experimentos.

O catálogo é histórico: o produto não promete estoque, compra, entrega atual ou preço em reais. O objetivo é demonstrar engenharia de IA, análise e produto com evidências que o candidato saiba explicar; não existe garantia de aprovação na seleção.
