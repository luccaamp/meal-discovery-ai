# Automação n8n planejada

Ainda não existe workflow exportado ou execução real.

Fluxo proposto: gatilho manual → consultar API própria de resultados de avaliação concluída → validar run_id/esquema → consolidar comparação com execução anterior → gerar relatório Markdown local. Não executar treinamento longo dentro de uma chamada síncrona do n8n.

O relatório informa versões, amostra, métricas, falhas e custo. Sinalizar regressões só quando houver referência comparável e limiar documentado. Testar falha da API, execução duplicada e credencial inválida. Não enviar mensagens a terceiros automaticamente.

Ao implementar: versionar export JSON sanitizado, parâmetros de ambiente, instruções de importação, capturas de execução e tempo manual/automatizado. Credenciais permanecem no armazenamento local da ferramenta.
