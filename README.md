# InvestWallet — versão web integrada

Aplicação de gestão de carteira e analytics com Streamlit, Python e SQLite. Mantém o banco existente e os módulos legados em `legacy/` como referência; a interface web utiliza serviços novos e não executa os scripts legados automaticamente.

## Requisitos
- Python 3.10+
- Dependências: `pip install -r requirements.txt`
- Copie `.env.example` para `.env` se precisar configurar o banco.

## Banco de dados
O caminho padrão é `data/mercado.db`. Para outro caminho, configure `DB_PATH` no `.env`. Caminhos relativos são interpretados a partir da raiz do projeto.

**Antes de atualizar uma instalação existente, faça uma cópia de segurança de `data/mercado.db`.** As migrações são aditivas; não apagam movimentações, carteira ou histórico.

## Executar
Na raiz do projeto:

```bash
streamlit run app/main.py
```

## Funcionalidades
- **Dashboard:** posições em moeda nativa, totais por moeda e conversão consolidada apenas quando há câmbio e cobertura completa de cotações. Totais incompletos são identificados, não apresentados como patrimônio total.
- **Ativos:** cadastro com mercado, bolsa e moeda.
- **Movimentações:** registro de compras e vendas, validação de saldo disponível e recálculo do preço médio ponderado a partir do histórico.
- **Cotações e câmbio:** coleta do último candle diário disponível no Yahoo Finance para os ativos ativos cadastrados; grava histórico de cotações sem sobrescrever registros anteriores. Taxa USD/BRL informada manualmente.
- **Analytics:** estatísticas descritivas e gráficos com base nos dados existentes em `historico_diario`.

## Coleta de preços
A coleta usa `yfinance` e depende de acesso à internet e disponibilidade do Yahoo Finance. O preço é o último fechamento diário retornado, não necessariamente uma cotação intradiária em tempo real. Ativos brasileiros são consultados com sufixo `.SA` quando ainda não o possuem; ativos dos EUA são consultados pelo ticker cadastrado.

## Moedas
- Mercado `BR` usa moeda `BRL`.
- Mercado `US` usa moeda `USD`.
- O dashboard não soma moedas diferentes sem conversão.
- O câmbio é cadastrado manualmente na página **Cotações e câmbio**; informe uma taxa e confira sua data/fonte.

## Estrutura
- `app/pages`: interface Streamlit
- `app/services`: regras de negócio
- `app/repositories`: acesso SQLite
- `app/collectors`: integração de cotações
- `app/database`: conexão e migrações
- `legacy`: cópias dos módulos originais, preservadas como referência
- `tests`: testes automatizados

## Observações
- Os módulos em `legacy/` foram mantidos, mas não são chamados pela aplicação web. Alguns scripts originais possuem imports e operações que precisam de adaptação antes de serem executados isoladamente.
- O Yahoo Finance pode limitar requisições ou não fornecer dados para certos tickers. A página de coleta mostra sucesso/erro por ativo.
- Analytics é descritivo e não constitui recomendação de investimento.

## Atualização do pacote sem substituir o banco
O pacote de código distribuído não inclui arquivos SQLite. Ao atualizar uma instalação existente, extraia os arquivos do pacote sobre a pasta do projeto, mantendo seu `data/mercado.db` atual. Faça backup antes de iniciar a versão atualizada.
