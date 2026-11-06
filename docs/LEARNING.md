# Entender esta primeira implementação

## O que estamos construindo

Um sistema que sugere refeições a partir de compras anteriores e permite buscar opções por conversa. Os dados publicados pela Delivery Hero serão a matéria-prima. A interface mostrará o produto; os experimentos mostrarão a qualidade e os limites.

## Por que começar pelos dados

Para recomendar, precisamos saber quais itens existem e quais compras aconteceram. Se a ligação entre produto, estabelecimento e pedido estiver errada, o sistema aprenderá padrões errados. O comando `prepare` verifica essas relações antes de criar a base de análise.

## Como as primeiras sugestões funcionam

- Popularidade: sugerir itens frequentes nas compras passadas.
- Repetição: sugerir o que aquele perfil costuma comprar.
- Similaridade: usar itens comprados por pessoas com histórico parecido.

Essas referências permitem testar se uma solução mais sofisticada realmente acrescenta qualidade. O assistente de linguagem e os embeddings serão componentes próprios nas próximas etapas.

## Como conferimos se funciona

Usamos compras antigas para montar os perfis. Guardamos compras posteriores para verificar se os itens comprados aparecem entre as sugestões. A compra futura nunca deve ajudar a construir o perfil que será avaliado.

Os exemplos sintéticos são pequenos registros inventados para testar o código, como testes de uma calculadora com números conhecidos. Eles não comprovam desempenho em pessoas ou operações reais. O relatório deixa essa distinção explícita.

## Exercício de compreensão

No teste automatizado, um perfil novo compra um item que não aparece no treino. Confira no código por que ele conta como erro e por que removê-lo do cálculo melhoraria artificialmente a métrica. Depois, localize o teste que adiciona compras futuras sem alterar a validação anterior. Esse cenário fica só nos testes; produto e experimentos usam dados reais.
