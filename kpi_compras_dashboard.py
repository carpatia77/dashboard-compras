import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime

# Configuração do estilo
plt.style.use('default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 100  # Melhor qualidade para web

# --- Funções Auxiliares ---
def parse_date(date_str):
    """Converte string de data para datetime com tratamento robusto"""
    if pd.isna(date_str) or not isinstance(date_str, str):
        return pd.NaT
    date_str = date_str.strip().upper()
    if "COTAÇÃO" in date_str or "EM COTAÇÃO" in date_str:
        return pd.NaT
    try:
        # Tenta converter no formato DD/MM/YYYY
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        return pd.NaT

def format_currency(value):
    """Formata valor monetário para padrão brasileiro"""
    if pd.isna(value) or value == 0:
        return "R$ 0,00"
    return f"R$ {abs(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_status_color(economia):
    """Define cor baseada no valor de economia"""
    return '#2ecc71' if economia >= 0 else '#e74c3c'  # Verde para economia, vermelho para gasto extra

# --- Dados ---
dados_cotacoes = {
    'Cliente': ['NAIC', 'NAIC', 'NAIC', 'NAIC', 'NAIC', 'Cabinda – OECRC ou BPCRC', 'NAIC', 
                'Cabinda – OECRC ou BPCRC', 'NAIC', 'NAIC', 'NAIC', 'Cabinda – OECRC ou BPCRC', 
                'NAIC', 'NAIC', 'Refinaria do Lobito – OECRL ou BPCRL', 'Cabinda – OECRC ou BPCRC', 
                'NAIC', 'Refinaria de Cabinda – COR', 'Refinaria de Cabinda – COR', 
                'Refinaria de Cabinda – COR', 'Refinaria de Cabinda – COR', 'Refinaria de Cabinda – COR', 
                'QGMI', 'QGMI'],
    'Referencia': ['505', '518', '534', '530', '538', '8380', '537', '34', '555', '548', 
                  'NOTEBOOK DELL PRO 14 PREMIUM GL', '8552', '573', '569', 'Cerca de Vedação Interna', 
                  '8610', '586', '00018', '00060', '00064', '00068', '00069', 'PR5551', 'PR5553'],
    'Data_Cotacao': ['01/08/2025', '01/08/2025', '05/08/2025', '05/08/2025', '06/08/2025', 
                    '07/08/2025', '05/08/2025', '13/08/2025', '14/08/2025', '14/08/2025', 
                    '18/08/2025', '19/08/2025', '25/08/2025', '25/08/2025', '26/08/2025', 
                    '27/08/2025', '27/08/2025', '06/08/2025', '07/08/2025', '12/08/2025', 
                    '15/08/2025', '15/08/2025', '27/08/2025', '27/08/2025'],
    'Data_Mapa': ['05/08/2025', '04/08/2025', '11/08/2025', '22/08/2025', '22/08/2025', 
                 'em cotação', '07/08/2025', '14/08/2025', '20/08/2025', '21/08/2025', 
                 '18/08/2025', 'em cotação', '25/08/2025', '26/08/2025', 'em cotação', 
                 '28/08/2025', '28/08/2025', '06/08/2025', '07/08/2025', '22/08/2025', 
                 '20/08/2025', 'em cotação', '27/08/2025', '29/08/2025'],
    'Data_PFI': ['06/08/2025', '05/08/2025', '13/08/2025', '27/08/2025', '25/08/2025', 
                'EM COTAÇÃO', '08/08/2025', '18/08/2025', '21/08/2025', '29/08/2025', 
                '20/08/2025', 'EM COTAÇÃO', '26/08/2025', 'PERGUNTAR ALE', 'EM COTAÇÃO', 
                '01/09/2025', '28/08/2025', '11/08/2025', '11/08/2025', '27/08/2025', 
                '25/08/2025', 'em cotação', '28/08/2025', '01/09/2025']
}

dados_compras = {
    'Cliente': ['COR', 'COR', 'COR', 'COR', 'COR', 'COR', 'NAIC', 'Refinaria do Lobito', 'NAIC'],
    'PFI': ['379', '379', '379', '379', '377', '393', '449', '132', '537'],
    'Produto': ['EPI', 'EPI', 'EPI', 'EPI', 'REPELENTES', 'MEDIDORES DE GASES', 'VERGALHAO', 'VALVULAS', 'ARAME RECOZIDO'],
    'Preco_Cotado': [260, 487, 7276.53, 10880.55, 10763.77, 37027.79, 87161.85, 28425.78, 3542.50],
    'Preco_Comprado': [260, 487, 6993.59, 10640, 10763.77, 37027.79, 87161.85, 28425.78, 3542.50]
}

# --- Processamento de Dados ---
# Convertendo dados de cotações
df_cotacoes = pd.DataFrame(dados_cotacoes)

# Tratamento robusto de datas
df_cotacoes['Data_Cotacao_DT'] = df_cotacoes['Data_Cotacao'].apply(parse_date)
df_cotacoes['Data_Mapa_DT'] = df_cotacoes['Data_Mapa'].apply(parse_date)
df_cotacoes['Data_PFI_DT'] = df_cotacoes['Data_PFI'].apply(parse_date)

# Calculando status real das cotações
df_cotacoes['Status'] = df_cotacoes['Data_Mapa_DT'].apply(
    lambda x: 'Concluída' if pd.notna(x) else 'Em Cotação'
)

# Calculando tempo de processamento (apenas para concluídas)
df_cotacoes['Dias_Processamento'] = (
    (df_cotacoes['Data_Mapa_DT'] - df_cotacoes['Data_Cotacao_DT']).dt.days
)

# Processando dados de compras com lógica CORRETA de economia
df_compras = pd.DataFrame(dados_compras)
df_compras['Economia'] = df_compras['Preco_Cotado'] - df_compras['Preco_Comprado']  # CORREÇÃO AQUI!
df_compras['Desconto'] = (df_compras['Economia'] / df_compras['Preco_Cotado']) * 100

# Calculando métricas principais
total_economia = df_compras['Economia'].sum()
total_cotacoes = len(df_cotacoes)
cotacoes_concluidas = len(df_cotacoes[df_cotacoes['Status'] == 'Concluída'])
cotacoes_andamento = len(df_cotacoes[df_cotacoes['Status'] == 'Em Cotação'])
maior_economia = df_compras['Economia'].max()
maior_desconto = df_compras['Desconto'].max()
gasto_extra = df_compras[df_compras['Economia'] < 0]['Economia'].sum()

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="Dashboard KPIs Compras", 
    layout="wide",
    page_icon="💰"
)

# Estilo personalizado - AJUSTADO PARA SCORECARDS VISÍVEIS E SUBTÍTULOS COM CORES FORTES
st.markdown("""
<style>
    /* Correção para os subtítulos dos scorecards - CORES FORTES */
    h2 {
        color: #0d47a1 !important;  /* Azul royal forte */
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        border-bottom: 2px solid #1976d2;
        padding-bottom: 8px;
    }
    
    /* Estilo para os cards de métricas do Streamlit */
    div[data-testid="stMetricValue"] {
        color: #1a237e !important;  /* Azul escuro intenso */
        font-weight: bold;
        font-size: 1.2em;
    }
    div[data-testid="stMetricLabel"] {
        color: #0d47a1 !important;  /* Azul royal forte para rótulos */
        font-weight: bold;
        font-size: 0.95em;
    }
    .stMetric {
        background-color: #e3f2fd;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        border: 2px solid #90caf9;
        margin-bottom: 10px;
        transition: transform 0.2s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    .warning {
        background-color: #fff8e1;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9em;
        border-top: 1px solid #eee;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Título e Introdução ---
st.title("📊 KPIs do Departamento de Compras - Agosto/2025")
st.markdown("""
<div class="info-box" style="background-color: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <strong style="color: #1565c0; font-size: 1.1em;">Definições importantes:</strong><br>
    • <strong style="color: #0d47a1;">Economia</strong> = Preço Cotado - Preço Comprado (valores positivos = economia real)<br>
    • <strong style="color: #0d47a1;">Cotação concluída</strong> = Quando há data registrada no MAPA<br>
    • <strong style="color: #0d47a1;">Tempo de processamento</strong> = Dias entre a data de cotação e data no MAPA
</div>
""", unsafe_allow_html=True)

# --- Métricas Principais ---
st.subheader("📌 Métricas Principais")

col1, col2, col3 = st.columns(3)

col1.metric("Cotações Realizadas", total_cotacoes)
col2.metric("Cotações Concluídas", cotacoes_concluidas)
col3.metric("Cotações em Andamento", cotacoes_andamento)

col1.metric("Economia Total", format_currency(total_economia), 
           help="Soma das economias (valores positivos = economia real)")
col2.metric("Maior Economia", format_currency(maior_economia),
           help="Maior valor economizado em uma compra")
col3.metric("Maior Desconto", f"{maior_desconto:.1f}%" if maior_desconto > 0 else "0.0%",
           help="Maior redução percentual sobre preço cotado")

if gasto_extra < 0:
    st.markdown(f"""
    <div class="warning">
        ⚠️ Alerta: {format_currency(abs(gasto_extra))} em gasto extra detectado! 
        Algumas compras foram feitas acima do preço cotado.
    </div>
    """, unsafe_allow_html=True)

# --- Gráficos ---
st.subheader("📊 Análise Detalhada")

# Gráfico 1: Status das Cotações - DIMENSÃO REDUZIDA EM 30%
st.markdown("### **Status das Cotações**")
fig1, ax1 = plt.subplots(figsize=(3.5, 2.1))  # Reduzido em 30% (era 5x3)
status_counts = df_cotacoes['Status'].value_counts()
colors = ['#2ecc71', '#3498db']  # Verde para concluídas, azul para em andamento
ax1.pie(status_counts, labels=status_counts.index, autopct='%1.0f%%', 
        colors=colors, startangle=90, explode=[0.05, 0])
ax1.set_title('Distribuição de Status das Cotações', fontsize=10, fontweight='bold', color='#2c3e50')
st.pyplot(fig1)

# Gráfico 2: Economia por Categoria - DIMENSÃO REDUZIDA EM 30%
st.markdown("### **Economia por Categoria de Produto**")
fig2, ax2 = plt.subplots(figsize=(4.2, 2.5))  # Reduzido em 30% (era 6x3.5)
categorias = df_compras['Produto'].unique()
economia_categorias = [df_compras[df_compras['Produto'] == cat]['Economia'].sum() for cat in categorias]
colors = [get_status_color(e) for e in economia_categorias]

ax2.barh(categorias, economia_categorias, color=colors)
ax2.axvline(0, color='k', linewidth=0.8)
ax2.set_xlabel('Valor da Economia (R$)', fontsize=9, color='#2c3e50')
ax2.set_title('Economia por Categoria de Produto', fontsize=11, fontweight='bold', color='#2c3e50')

# Adicionar valores nas barras
for i, v in enumerate(economia_categorias):
    ax2.text(v + (18 if v >= 0 else -18), i, format_currency(v), 
             va='center', ha='left' if v >= 0 else 'right', fontweight='bold', fontsize=8, color='#2c3e50')

st.pyplot(fig2)

# Gráfico 3: Economia por Cliente - DIMENSÃO REDUZIDA EM 30%
st.markdown("### **Economia por Cliente**")
fig3, ax3 = plt.subplots(figsize=(4.2, 2.5))  # Reduzido em 30% (era 6x3.5)
clientes = df_compras['Cliente'].unique()
economia_clientes = [df_compras[df_compras['Cliente'] == cliente]['Economia'].sum() for cliente in clientes]
colors = [get_status_color(e) for e in economia_clientes]

ax3.bar(clientes, economia_clientes, color=colors)
ax3.axhline(0, color='k', linewidth=0.8)
ax3.set_ylabel('Valor da Economia (R$)', fontsize=9, color='#2c3e50')
ax3.set_title('Economia por Cliente', fontsize=11, fontweight='bold', color='#2c3e50')

# Adicionar valores nas barras
for i, v in enumerate(economia_clientes):
    ax3.text(i, v + (18 if v >= 0 else -18), format_currency(v), 
             ha='center', va='bottom' if v >= 0 else 'top', fontweight='bold', fontsize=8, color='#2c3e50')

plt.xticks(rotation=15, fontsize=8, color='#2c3e50')
plt.yticks(fontsize=8, color='#2c3e50')
st.pyplot(fig3)

# Gráfico 4: Distribuição de Cotações por Cliente - DIMENSÃO REDUZIDA EM 30%
st.markdown("### **Distribuição de Cotações por Cliente**")
fig4, ax4 = plt.subplots(figsize=(4.2, 2.5))  # Reduzido em 30% (era 6x3.5)
clientes_cotacoes = df_cotacoes['Cliente'].value_counts()
colors = plt.cm.Paired(np.linspace(0, 1, len(clientes_cotacoes)))

ax4.pie(clientes_cotacoes.values, labels=clientes_cotacoes.index, autopct='%1.0f%%', 
        colors=colors, startangle=90, textprops={'fontsize': 8, 'color': '#2c3e50'})
ax4.set_title('Participação por Cliente nas Cotações', fontsize=11, fontweight='bold', color='#2c3e50')
st.pyplot(fig4)

# Gráfico 5: Tempo de Processamento - DIMENSÃO REDUZIDA EM 30%
st.markdown("### **Tempo de Processamento das Cotações**")
concluidas = df_cotacoes[df_cotacoes['Status'] == 'Concluída'].nlargest(10, 'Dias_Processamento')
if not concluidas.empty:
    fig5, ax5 = plt.subplots(figsize=(4.2, 2.5))  # Reduzido em 30% (era 6x3.5)
    
    # Criar cores baseadas no tempo (verde para rápido, vermelho para lento)
    max_dias = max(concluidas['Dias_Processamento'])
    colors = [plt.cm.RdYlGn(1 - x/max_dias) for x in concluidas['Dias_Processamento']]
    
    ax5.barh(concluidas['Referencia'], concluidas['Dias_Processamento'], color=colors)
    ax5.set_xlabel('Dias para conclusão', fontsize=9, color='#2c3e50')
    ax5.set_title('Top 10 Cotações com Maior Tempo de Processamento', fontsize=11, fontweight='bold', color='#2c3e50')
    
    # Adicionar valores nas barras
    for i, v in enumerate(concluidas['Dias_Processamento']):
        ax5.text(v + 0.2, i, f"{v} dias", va='center', fontsize=8, color='#2c3e50')
    
    plt.yticks(fontsize=8, color='#2c3e50')
    st.pyplot(fig5)
else:
    st.info("Nenhuma cotação concluída para análise de tempo de processamento")

# --- Tabela de Detalhes ---
st.subheader("📋 Detalhes das Compras")

# Adicionar colunas formatadas
df_display = df_compras.copy()
df_display['Economia_Format'] = df_display['Economia'].apply(format_currency)
df_display['Desconto_Format'] = df_display['Desconto'].apply(lambda x: f"{x:.1f}%" if x > 0 else "0.0%")

# Configurar cores para a tabela
def color_economia(val):
    color = '#2ecc71' if float(val) >= 0 else '#e74c3c'
    return f'color: {color}; font-weight: bold'

# Exibir tabela com formatação
st.dataframe(
    df_display[['Cliente', 'Produto', 'Preco_Cotado', 'Preco_Comprado', 'Economia_Format', 'Desconto_Format']]
    .rename(columns={
        'Preco_Cotado': 'Preço Cotado',
        'Preco_Comprado': 'Preço Comprado',
        'Economia_Format': 'Economia',
        'Desconto_Format': 'Desconto'
    }),
    column_config={
        "Preço Cotado": st.column_config.NumberColumn(
            "Preço Cotado",
            format="R$ %.2f",
        ),
        "Preço Comprado": st.column_config.NumberColumn(
            "Preço Comprado",
            format="R$ %.2f",
        )
    },
    hide_index=True,
    use_container_width=True
)

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div class="footer">
    Dashboard KPIs de Compras • Dados simulados para Agosto/2025 • 
    Atualizado em tempo real com os dados mais recentes do sistema
</div>
""", unsafe_allow_html=True)
