# Dados

Fonte original: [Delivery Hero Recommendation Dataset](https://github.com/deliveryhero/dh-reco-dataset). O README declara MIT e aponta para uma pasta que exige autorização. Já obtivemos a [cópia pública derivada dos autores do HyperHawkes](https://github.com/dbis-uibk/HyperHawkes), com 740.707 interações e nomes reais de itens. Ver [procedência, hashes e limites](../docs/DATA_ACCESS.md). Ela está em `data/raw/hyperhawkes-dhrd/`, fora do Git.

O artigo descreve pedidos, produtos e vendedores de três cidades. Há preços normalizados, nomes multilíngues, IDs anonimizados e geografia aproximada. Não há garantia de fotos, ingredientes, alérgenos, estoque atual ou tempo de entrega.

Diretórios locais futuros: `raw/`, `interim/`, `processed/`. Todos ignorados pelo Git. Não publicar dados corporativos, currículo ou transcrições privadas.

Ao obter a base: registrar data, URL, versão, hashes, licença, esquema real, contagens por cidade e split. Conferir duplicatas, unidades, relações de tabelas, cobertura temporal, IDs órfãos e cardinalidade. O comando `prepare` já valida um contrato relacional explícito em CSV e cria SQLite; esse contrato ainda não foi testado com os arquivos DHRD. Ver [pipeline](../docs/DATA_PIPELINE.md) e [acesso](../docs/DATA_ACCESS.md).
