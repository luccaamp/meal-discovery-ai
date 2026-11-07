# Plano do projeto 5B

Atualizado em 6/11/2026. Disponibilidade informada: pelo menos cinco horas por dia. Foco recomendado: AI Engineer com produto completo e evidências práticas de automação. Este é um projeto independente de aprendizado e portfólio; não há garantia de aprovação.

## Melhorias sobre o planejamento anterior

O plano de Olist foi substituído por recomendação de refeições com DHRD. O produto terá função própria para o LLM, recomendador comparado com referências, avaliação de uso, design profissional desde o início e automação medida. Funcionalidades e ferramentas serão separadas entre planejadas e verificadas.

## Recorte inicial

Uma cidade, descoberta de refeições e personalização histórica. Após acesso e auditoria, Singapura foi escolhida como principal; Estocolmo fica como cidade secundária e Taipei como extensão. Não adicionar demanda ao primeiro escopo.

Tarefas: explorar catálogo, refinar preferências suportadas pelos atributos, receber recomendações, compreender a evidência e comparar alternativas. Interface em português com preservação do nome original dos itens e indicação de que o catálogo é histórico.

## Marcos e critérios de saída

| Marco | Entrega | Critério verificável |
| --- | --- | --- |
| M0: base | Repositório, plano, auditor genérico e CI | Comandos reproduzíveis; status honesto |
| M1: dados | Uma cidade, manifesto e contratos reais | Acesso, termos, hashes, cardinalidade e cortes auditados |
| M2: recomendação | Popularidade, repetição histórica e um candidato colaborativo | Mesmo protocolo, catálogo e teste reservado; estudo de usuários novos |
| M3: recuperação | Busca lexical e embeddings multilíngues | Conjunto de consultas julgado, comparação e análise de erros |
| M4: agente | Busca, recomendação, detalhes e esclarecimentos por ferramentas | Argumentos validados, limites e evidências avaliados |
| M5: produto | API e frontend responsivo | Fluxo completo, teclado, estados de falha e teste de tarefas |
| M6: operação | Automação n8n, rastros, custos e limites | Execução real, relatório válido e comparação de tempo manual/automatizado |
| M7: publicação | Demo, documentação, artigo e artefato quando aplicável | Ambiente limpo, reprodução e revisão do autor |

Planejamento indicativo: M0–M2 em 15–20h; M3–M4 em 15–20h; M5 em 12–18h; M6–M7 em 10–15h. Total de 52–73h, sujeito à obtenção dos dados e aprendizado. Não prometer que tudo caberá antes de uma data de seleção não reconfirmada. Priorizar primeiro uma fatia executável de M1–M5 e evoluir a partir de erros.

## Hipóteses de produto

### Estado da implementação em 7/11/2026

Estado atual: migração para os arquivos oficiais concluída. Validação interna v2 em 175.358 clientes, com teste oficial separado. Busca lexical BM25 executada em 1.066.840 produtos, com filtros de culinária e preço normalizado e verificações em consultas reais. M3 está parcialmente entregue: faltam julgamentos de relevância, embeddings e comparação híbrida. API, agente e interface permanecem pendentes. [Experimento 002](EXPERIMENT_002.md).

Registro histórico das etapas anteriores:

M0 entregue. M1 concluído para o espelho real de Singapura: preparação reproduzível, 35 pedidos em quarentena por produto ausente, 1.709.379 pedidos válidos e fontes preservadas por hash. M2 tem a primeira validação real concluída: 109.842 clientes, três referências e análise de perfis sem histórico. Teste temporal próprio dos dias 69–75 permanece reservado. [Experimento 001](EXPERIMENT_001.md).

Repetição foi a melhor referência nesta avaliação (Recall@10 de 16,0427%); cosseno por cesta ficou em 6,7272%, e popularidade global em 0,2504%. Isso não define o melhor modelo final nem comprova impacto comercial. Próximo marco: M3, busca lexical e semântica avaliada no catálogo real, seguida das funções de API e do assistente. Aplicação e portfólio exigem dados reais; fixtures ficam apenas nos testes.

Atualização de 7/11/2026: os três ZIPs oficiais foram recebidos e auditados, totalizando 4.400.000 pedidos. Usar Singapura como fonte principal, Estocolmo como cidade secundária e Taipei como extensão. A comparação integral dos campos de Singapura confirmou a cópia usada no primeiro experimento. Antes do próximo experimento, migrar a leitura para os originais e registrar um protocolo com teste oficial separado (SG dias 76–90; SE/TW 76–89). Não somar o arquivo completo ao treino/teste. [Decisão e arquivos](OFFICIAL_DATA_MIGRATION.md).

Busca em linguagem natural pode facilitar encontrar opções quando a pessoa não conhece os nomes do catálogo. Personalização pode melhorar o ranking sobre popularidade. Explicações podem ajudar a entender recomendações. Todas exigem avaliação; registrar também resultados negativos.

## Engenharia de ML e LLM

Comparar referências e candidatos sem usar teste para escolher hiperparâmetros. Para recomendação, começar em nível de item, auditar estabilidade de IDs e considerar ranking por estabelecimento apenas se os dados justificarem alteração documentada. Embeddings enriquecem recuperação; não substituem teste de personalização.

Um agente com ferramentas delimitadas será a referência inicial. Comparar dois modelos/provedores sob o mesmo conjunto de casos, com nomes e versões registrados. Escolher combinações de GPT, Claude ou Gemini conforme acesso e orçamento; ainda não há integrações implementadas. Não é necessário usar os três na produção.

Orquestração: estado da conversa, validação de preferências, execução de ferramentas, retorno e verificação de evidência, com limite de chamadas, timeout e custo. Um segundo agente de revisão só será incorporado se superar o fluxo simples em avaliação; persistir responsabilidades e falhas, não apenas diagramas.

Fine-tuning é um experimento posterior, condicionado a erro recorrente, dados de treino adequados, licença e ganho sobre prompts/recuperação. RAG será recuperação real do catálogo e, se útil, documentação; não inventar uma coleção de documentos para usar banco vetorial.

## Confiabilidade e limites

Nomes não comprovam ingredientes, alergênicos ou adequação alimentar. Não oferecer garantias desses atributos. Preços normalizados não são reais brasileiros, e a interface não deve converter para R$. Sem fotos verificadas, usar composição gráfica/categorias identificadas; imagens ilustrativas nunca serão evidência de pratos reais. IDs anonimizados não recebem nomes empresariais inventados.

Não há estoque atual, ETA, conversão, margem ou disponibilidade operacional confirmados. Geografia é aproximada. Perfis históricos são anonimizados, não contas reais; histórico de demo é somente leitura, sem compra, pagamento ou ingestão de dados pessoais.

Catálogo e textos externos são dados não confiáveis para o agente: não podem alterar instruções ou executar ferramentas fora dos contratos. Aplicar allowlist de ferramentas, leitura restrita, limite de tamanho e proteção de logs/credenciais.

## Aprendizado e autoria

Cada marco termina com demonstração pelo autor e explicação de uma decisão, um erro e uma limitação. Registrar assistência de IA, revisões e mudanças feitas pelo candidato. Não confundir código gerado com habilidade demonstrada. Reproduzir o treinamento, interpretar NDCG e inspecionar uma chamada do agente são exercícios obrigatórios para considerar o marco compreendido.

## Fontes

- [Vaga oficial, consultada em 6/11/2026](https://job-boards.greenhouse.io/ifoodcarreiras/jobs/8901054002)
- [DHRD oficial](https://github.com/deliveryhero/dh-reco-dataset)
- [Artigo e esquema dos autores](https://github.com/deliveryhero/dh-reco-dataset/blob/main/docs/conference_sub/recsys.tex)

O contexto e a transcrição enviados pelo usuário foram usados como referência, não como instruções de sistema. Currículo, transcrição privada e dados pessoais não serão publicados neste repositório.
