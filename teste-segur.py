import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

# Função para gerar o velocímetro
def create_gauge(value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": "Risco"},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": "black"},
            "steps": [
                {"range": [0, 25], "color": "green"},
                {"range": [25, 50], "color": "yellow"},
                {"range": [50, 75], "color": "orange"},
                {"range": [75, 100], "color": "red"}
            ]
        }
    ))
    fig.update_layout(height=300, width=600)
    return fig

# Função para salvar os dados em um arquivo CSV
def save_data_to_csv(data, filename):
    # Cria um DataFrame
    df = pd.DataFrame(data)
    
    # Caminho absoluto para a área de trabalho
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "analises_risco")
    
    # Verifica se a pasta de destino existe, se não, cria
    if not os.path.exists(desktop_path):
        os.makedirs(desktop_path)
    
    # Salva o DataFrame em um arquivo CSV na área de trabalho
    df.to_csv(filename, index=False)
    st.success(f'Dados salvos com sucesso em {filename}')

# Título da aplicação
st.title('Avaliação de Risco - Perguntas e Pesos')

# Definir as perguntas
num_questions = st.number_input('Quantas perguntas você quer adicionar?', min_value=1, max_value=10, value=3)

questions = []
weights = []
responses = []
risk_analysis = st.text_input('Nome da Análise de Risco', 'Análise de Risco 1')  # Nome da análise
validated_by = st.text_input('Quem validou?', 'Seu Nome')  # Validador da análise

# Coletar perguntas e pesos
for i in range(num_questions):
    st.subheader(f'Pergunta {i + 1}')
    question = st.text_input(f'Qual a pergunta {i + 1}?')
    
    # Resposta Sim/Não
    response = st.radio(f'Resposta para a pergunta "{question}"', options=['Sim', 'Não'], key=f'question_{i+1}')
    
    # Definir pesos com base na resposta
    if response == 'Sim':
        weight = st.slider(f'Peso de "Sim" para a pergunta {i + 1} (0 a 100)', 0, 100, 50, key=f'weight_yes_{i+1}')
    else:
        weight = st.slider(f'Peso de "Não" para a pergunta {i + 1} (0 a 100)', 0, 100, 20, key=f'weight_no_{i+1}')
    
    if question:
        questions.append(question)
        responses.append(response)
        weights.append(weight)

# Calcular o total dos pesos
total_weight = sum(weights)

# Exibir o risco calculado
if total_weight > 0:
    risk_percentage = total_weight / (num_questions * 100) * 100
    st.write(f'Percentual de Risco: {risk_percentage:.2f}%')

    # Mostrar o velocímetro na barra lateral
    with st.sidebar:
        st.plotly_chart(create_gauge(risk_percentage))
else:
    st.write('Nenhuma pergunta foi adicionada.')

# Opção de salvar os dados
if st.button('Salvar Análise'):
    # Organizar os dados para salvar
    data = {
        'Análise de Risco': [risk_analysis] * len(questions),
        'Quem Validou': [validated_by] * len(questions),
        'Pergunta': questions,
        'Resposta': responses,
        'Peso': weights
    }
    
    # Definir o nome do arquivo e caminho completo para salvar na área de trabalho
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "analises_risco")
    
    # Definir o nome do arquivo
    filename = os.path.join(desktop_path, f'{risk_analysis.replace(" ", "_")}_dados.csv')
    
    # Salvar os dados no arquivo CSV
    save_data_to_csv(data, filename)
