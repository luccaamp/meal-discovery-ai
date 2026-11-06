# Dados

Fonte: [Delivery Hero Recommendation Dataset](https://github.com/deliveryhero/dh-reco-dataset). O README da fonte declara licença MIT e aponta para uma pasta de download. Acesso efetivo aos arquivos ainda não confirmado; conferir termos que acompanham o download.

O artigo descreve pedidos, produtos e vendedores de três cidades. Há preços normalizados, nomes multilíngues, IDs anonimizados e geografia aproximada. Não há garantia de fotos, ingredientes, alérgenos, estoque atual ou tempo de entrega.

Diretórios locais futuros: `raw/`, `interim/`, `processed/`. Todos ignorados pelo Git. Não publicar dados corporativos, currículo ou transcrições privadas.

Ao obter a base: registrar data, URL, versão, hashes, licença, esquema real, contagens por cidade e split. Conferir duplicatas, unidades, relações de tabelas, cobertura temporal, IDs órfãos e cardinalidade. O auditor inicial inventaria apenas CSVs; não implementa essas validações específicas ainda.
