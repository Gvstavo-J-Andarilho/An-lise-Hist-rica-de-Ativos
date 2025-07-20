import yfinance as yf
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import openpyxl
import os
import numpy as np

# === Pergunta tipo de ativo ===
tipo_ativo = input("O ativo é BTC (digite 'btc') ou outro (ação/moeda)? ").strip().lower()
if tipo_ativo == 'btc' or tipo_ativo == 'b' or tipo_ativo=='bitcoin':
    ticker = 'BTC-USD'
    casas_decimais = 8
    taxa_saque_btc = 0.0005
else:
    ticker = input("Digite o ticker (ex: BTC-USD ou PETR4.SA): ").strip().upper()
    ticker = ticker + ".SA"
    casas_decimais = 0  # Ações e FIIs no Brasil: apenas inteiros
    taxa_saque_btc = 0

pd.options.display.float_format = f'{{:.{casas_decimais}f}}'.format

# === Função para obter dia útil próximo ao dia 5 ===
def obter_dia_util_mais_proximo(data, dia_alvo=5):
    ano = data.year
    mes = data.month
    dia_alvo_data = dt.date(ano, mes, dia_alvo)
    while dia_alvo_data.weekday() >= 5:
        dia_alvo_data += dt.timedelta(days=1)
    return dia_alvo_data

# === Parâmetros do ativo ===
data_inicial = '2023-01-01'
data_final = dt.date.today().strftime('%Y-%m-%d')

# === Baixar dados ===
df = yf.download(ticker, start=data_inicial, end=data_final)

# === Processar dados ===

df['MesAno'] = df.index.to_period('M')
df['Data'] = df.index.date
dias_uteis_mais_proximos = []
for mesano, grupo in df.groupby('MesAno'):
    primeiro_dia_mes = dt.date(grupo.index[0].year, grupo.index[0].month, 1)
    dia_5_proximo = obter_dia_util_mais_proximo(primeiro_dia_mes)
    dias_uteis_mais_proximos.append(dia_5_proximo)

df_filtrado = df[df['Data'].isin(dias_uteis_mais_proximos)].copy()
df_filtrado['Fechamento'] = df_filtrado['Close'].round(2)
df_final = df_filtrado[['Data', 'Fechamento']].copy()
df_final.reset_index(drop=True, inplace=True)

# === Mediana e dividendos simulados ===
mediana_fechamento = df_final['Fechamento'].median()
print(f"\n📊 Mediana dos preços de fechamento: {mediana_fechamento:.2f}")
print(f"📊 Dividendos simulados (6%): {mediana_fechamento * 0.06:.2f}\n")

# === Inputs do usuário ===
try:
    aporte_mensal = float(input("💵 Valor do aporte mensal (ex: 38 ou 200): "))
except:
    aporte_mensal = 200
    print("Valor inválido. Usando 200.")

try:
    taxa_percentual = float(input("📉 Taxa percentual por operação (ex: 0.5 para 0.5%): ")) / 100
except:
    taxa_percentual = 0.005
    print("Valor inválido. Usando 0.5%.")

# === Perguntar se o ativo paga dividendos (se não for BTC) ===
if tipo_ativo == 'btc':
    paga_dividendos = False
    print("❌ BTC não paga dividendos. Bola de neve desativada.")
else:
    resposta = input("🧾 Esse ativo paga dividendos? (s/n): ").strip().lower()
    paga_dividendos = resposta == 's'

# === Simulação com bola de neve (reinvestimento de dividendos) ===
if paga_dividendos:
    try:
        dy_anual_percentual = float(input("📈 Informe o Dividend Yield (DY) anual (%) estimado: "))
    except:
        dy_anual_percentual = 6
        print("Valor inválido. Usando 6% ao ano.")

    dy_mensal = dy_anual_percentual / 100 / 12
    dividendos_acumulados = 0
    qtd_acumulada = 0
    qtd_acumulada_lista = []
    qtd_liquida_lista = []

    for i, row in df_final.iterrows():
        dividendos_mes = qtd_acumulada * row['Fechamento'] * dy_mensal
        dividendos_acumulados += dividendos_mes

        aporte_total = aporte_mensal + dividendos_acumulados
        taxa = aporte_total * taxa_percentual
        aporte_liquido = aporte_total - taxa

        if tipo_ativo == 'btc':
            qtd_comprada = round(aporte_liquido / row['Fechamento'], 8)
        else:
            qtd_comprada = int((aporte_liquido / row['Fechamento']).item())

        qtd_acumulada += qtd_comprada
        qtd_liquida = max(qtd_acumulada - taxa_saque_btc, 0)

        df_final.at[i, 'Aporte'] = aporte_total
        df_final.at[i, 'Taxa'] = taxa
        df_final.at[i, 'Aporte_Liquido'] = aporte_liquido
        df_final.at[i, 'Qtd_Comprada_Bruta'] = qtd_comprada
        df_final.at[i, 'Qtd_Acumulada_Bruta'] = qtd_acumulada
        df_final.at[i, 'Qtd_Acumulada_Liquida'] = qtd_liquida

        dividendos_acumulados = 0  # reinvestido
else:
    df_final['Aporte'] = aporte_mensal
    df_final['Taxa'] = df_final['Aporte'] * taxa_percentual
    df_final['Aporte_Liquido'] = df_final['Aporte'] - df_final['Taxa']

    if tipo_ativo == 'btc':
        df_final['Qtd_Comprada_Bruta'] = (df_final['Aporte_Liquido'] / df_final['Fechamento']).round(8)
        df_final['Qtd_Acumulada_Bruta'] = df_final['Qtd_Comprada_Bruta'].cumsum().round(8)
    else:
        df_final['Qtd_Comprada_Bruta'] = (df_final['Aporte_Liquido'] / df_final['Fechamento']).astype(int)
        df_final['Qtd_Acumulada_Bruta'] = df_final['Qtd_Comprada_Bruta'].cumsum()

    df_final['Qtd_Acumulada_Liquida'] = df_final['Qtd_Acumulada_Bruta'] - taxa_saque_btc
    df_final['Qtd_Acumulada_Liquida'] = df_final['Qtd_Acumulada_Liquida'].clip(lower=0)

# === Exibir resumo ===
print("\n📈 Resumo dos dados acumulados:")
print(df_final[['Data', 'Fechamento', 'Qtd_Comprada_Bruta', 'Qtd_Acumulada_Bruta', 'Qtd_Acumulada_Liquida']])

# === Escolha de saída ===
opcao = input("\n📤 Você quer ver os dados como 'print', 'gráfico' ou 'imprimir' (para salvar em Excel)? ").strip().lower()

if opcao in ['print', 'p']:
    print(df_final)

elif opcao in ['grafico', 'g']:
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    media = 6
    media_movel = df_final['Fechamento'].rolling(window=media).mean()
    axs[0].plot(df_final['Data'], df_final['Fechamento'], label='Preço Fechamento', marker='o', color='blue')
    axs[0].plot(df_final['Data'], media_movel, label=f'Média Móvel {media} meses', color='orange')
    axs[0].set_title(f'{ticker} – Preço e Média Móvel {media} meses')
    axs[0].set_ylabel('Preço')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].step(df_final['Data'], df_final['Qtd_Acumulada_Liquida'], where='post', label='Qtd. Acumulada Líquida', color='green')
    axs[1].set_title('Quantidade Acumulada (Líquida)')
    axs[1].set_xlabel('Data')
    axs[1].set_ylabel('Qtd')
    axs[1].legend()
    axs[1].grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

elif opcao in ['imprimir', 'i']:
    nome_arquivo = f'{ticker}_fechamento_dia_util.xlsx'
    df_final.to_excel(nome_arquivo, index=False, float_format=f'%.{casas_decimais}f')
    print(f"\n✅ Arquivo Excel '{nome_arquivo}' criado com sucesso!")
    os.startfile(nome_arquivo)
else:
    print("❌ Opção inválida. Escolha: print, gráfico ou imprimir.")
