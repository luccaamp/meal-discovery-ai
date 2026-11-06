# Dados e primeira comparação de recomendação

## O que já executa

1. `audit`: inventário de CSVs.
2. `prepare`: valida arquivos com mapeamento explícito e cria um banco SQLite local.
3. `benchmark`: compara popularidade, repetição histórica e similaridade colaborativa de itens.
4. `scripts/fetch_hyperhawkes.py`: baixa a cópia pública real pré-processada do DHRD e verifica o hash.
5. `scripts/fetch_nearbite_sg.py` e `scripts/audit_nearbite_sg.py`: obtêm e auditam as três tabelas reais do espelho público de Singapura.

Nenhum resultado de recomendação em DHRD foi medido. O derivado de Estocolmo e três tabelas reais de Singapura estão disponíveis localmente. A auditoria de Singapura já examinou todas as tabelas e relações; a preparação para treino ainda precisa tratar o índice de exportação, dias textuais e 41 linhas com produto ausente no catálogo. O importador genérico abaixo ainda não incorpora essas transformações e não deve ser usado diretamente com os arquivos sem um adaptador explícito.

## Obter dados reais agora

Após a instalação descrita no README:

```sh
python scripts/fetch_hyperhawkes.py
```

Esse comando baixa o arquivo real para `data/raw/hyperhawkes-dhrd/` e registra procedência e auditoria. Ver [campos e limites](DATA_ACCESS.md). O comando de demonstração sintética foi removido; CLI de preparação e benchmark exigem dados reais. As fixtures artificiais existem apenas nos testes automatizados.

## Preparar dados reais quando disponíveis

1. Obter arquivos pela fonte oficial; registrar termos, cidade, nomes, tamanho, hashes e divisões fornecidas pelos autores.
2. Inspecionar o formato e os cabeçalhos. Se não forem CSVs compatíveis, implementar e testar uma conversão rastreável, preservando os arquivos originais.
3. Copiar `configs/source.example.json` para `configs/source.local.json` (ignorado pelo Git).
4. Substituir caminhos, cidade, licença e nomes das colunas pelos valores realmente observados. Cada caminho é relativo à pasta do JSON. Não usar o exemplo sem ajuste.
5. Executar a preparação, corrigindo ambiguidades na origem ou criando uma transformação documentada; o importador não remove silenciosamente órfãos ou escolhe um preço entre valores conflitantes.

```sh
python -m meal_discovery prepare --config configs/source.local.json --output data/processed/city-v1.sqlite
```

O manifesto fica dentro do banco na tabela `metadata`. Ele registra hashes, configuração, procedência declarada, período e contagens, sem publicar pedidos. `data_kind` vem da configuração: é um rótulo de procedência informado pelo operador, não certificação da autenticidade dos arquivos.

## Contrato de integridade

- Vendedor é único por `vendor_id`.
- Produto é único pelo par `(vendor_id, product_id)`, evitando colisões entre estabelecimentos.
- Pedido é único por `order_id` e tem cliente, dia relativo inteiro e horário local consistentes em todas as linhas.
- O horário deve ser representável como `HH:MM[:SS[.ffffff]]`; não interpretar automaticamente timestamps de formato desconhecido.
- Linhas do mesmo item no mesmo pedido são deduplicadas. A tarefa é presença de item na cesta, não quantidade.
- Referências a produtos e vendedores ausentes, chaves conflitantes, larguras inválidas, IDs vazios e preços não finitos são erros explícitos.
- Preço pode estar vazio. Valor observado é normalizado, sem conversão monetária.
- Arquivos são verificados por hash antes e depois da importação. O banco é publicado somente após validação; saída existente não é sobrescrita.

SQLite foi escolhido nesta etapa pelo suporte transacional e ausência de dependência extra. Parquet/DuckDB continuam opções futuras se os arquivos e o custo de processamento justificarem. A escolha não foi baseada em benchmark de escala real.

## Como avaliar sem usar o futuro

O comando exige `--train-end-day` e `--eval-end-day`; os cortes devem ser escolhidos após a auditoria, nunca copiados dos exemplos sintéticos. Treino usa todos os pedidos até o primeiro limite, inclusive; avaliação usa o período seguinte até o segundo limite, inclusive.

Para cada cliente, o alvo é sua primeira cesta no período de avaliação. O treino fica congelado: outras compras posteriores não atualizam o perfil. Empates são resolvidos por dia, horário e ID do pedido. Não há atualização progressiva neste protocolo inicial.

Referências:

- **Popularidade:** quantidade de cestas de treino contendo o item.
- **Repetição:** frequência do item nas cestas de treino do cliente, completada com popularidade.
- **Similaridade de itens:** cosseno entre conjuntos de compradores históricos, com redução de confiança para poucos compradores em comum. Somar similaridades aos vinte itens mais frequentes do perfil; completar com popularidade. Itens repetidos são permitidos.

Cada ranking tem IDs únicos e desempate determinístico. Métricas são médias por cliente: Recall@K, NDCG@K e Hit Rate@K. A relevância é binária por item; NDCG usa ganho 1/log2(posição+1). Há segmentos de clientes conhecidos/novos, cobertura do catálogo e latências p50/p95.

O catálogo candidato contém somente itens comprados no treino. Itens-alvo novos permanecem no denominador e contam como falhas. O relatório informa essa cobertura. Não há negativos amostrados nem filtro geográfico ainda; o experimento mede afinidade em catálogo histórico de uma cidade, sem comprovar disponibilidade ou possibilidade de entrega.

`--max-users` limita aos primeiros clientes por ordem cronológica e serve para testar execução/tempo. Esse recorte não é amostra representativa, nem resultado final de portfólio. A versão inicial calcula similaridade sob demanda e ordena o catálogo; escala ainda precisa de medição e otimização.

`--split validation` e `--split test` são rótulos no relatório. O programa não impede repetir consultas ao teste. Manter o teste reservado exige disciplina e registro das decisões. Resultados dos splits distribuídos pelos autores só serão comparados depois de entender seu protocolo.

Cada relatório inclui hashes da base, fontes e implementação, além do protocolo. Ainda não escolhemos hiperparâmetros, cidade nem cortes para DHRD.
