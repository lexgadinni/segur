import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from fpdf import FPDF
import tempfile
import requests

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

# Função para baixar a imagem do GitHub e salvar temporariamente
def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Garante que a resposta foi bem-sucedida
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, "logo.png")
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_path
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar a imagem: {e}")
        return None

# Função para contar o número de linhas de texto em uma célula (baseado na largura)
def get_num_lines(text, cell_width, pdf):
    pdf.set_font("Arial", '', 10)  # Definir fonte
    text_width = pdf.get_string_width(text)  # Calcular a largura do texto
    num_lines = text_width / cell_width  # Estimar o número de linhas necessárias
    return max(1, int(num_lines) + 1)  # Arredondar para cima o número de linhas

# Função para gerar o PDF com os dados ajustados
def generate_pdf(data, risk_analysis, validated_by, risk_percentage, logo_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Adicionar o logo, se disponível
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=30)

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Análise de Risco: {risk_analysis}", ln=True, align='C')

    pdf.ln(10)  # Linha em branco

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Validado por: {validated_by}", ln=True)

    pdf.ln(10)  # Linha em branco

    # Larguras das colunas
    question_width = 80
    response_width = 40
    weight_width = 40

    # Cabeçalho da tabela
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(question_width, 10, 'Pergunta', border=1, align='C')
    pdf.cell(response_width, 10, 'Resposta', border=1, align='C')
    pdf.cell(weight_width, 10, 'Peso', border=1, align='C')
    pdf.ln()

    # Adicionar dados à tabela
    pdf.set_font("Arial", '', 10)
    for question, response, weight in zip(data['Pergunta'], data['Resposta'], data['Peso']):
        # Calcular o número de linhas para a pergunta
        num_lines_question = get_num_lines(question, question_width, pdf)
        num_lines_response = get_num_lines(response, response_width, pdf)
        num_lines_weight = get_num_lines(str(weight), weight_width, pdf)
        line_height = 5  # Definir altura da linha

        # Adicionar a célula de pergunta com multi-cell para quebras de linha
        pdf.multi_cell(question_width, line_height, question, border=1)

        # Obter a posição atual após a pergunta
        x_current = pdf.get_x() + question_width
        y_current = pdf.get_y() - (num_lines_question * line_height)
        
        # Ajustar a altura das células de resposta
        pdf.set_xy(x_current, y_current)
        pdf.multi_cell(response_width, num_lines_response * line_height, response, border=1, align='C')

        # Ajustar a altura das células de peso
        x_next = pdf.get_x() + response_width
        pdf.set_xy(x_next, y_current)
        pdf.multi_cell(weight_width, num_lines_weight * line_height, str(weight), border=1, align='C')

        # Mover para a próxima linha após processar as três colunas
        pdf.ln(max(num_lines_question, num_lines_response, num_lines_weight) * line_height)

    # Adicionar o percentual de risco
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Percentual de Risco: {risk_percentage:.2f}%", ln=True)

    # Texto explicativo baseado no risco
    pdf.set_font("Arial", '', 12)
    if risk_percentage <= 25:
        pdf.multi_cell(0, 10, txt="Risco baixo: A análise indica que o risco está dentro de um nível aceitável. Não são necessárias ações urgentes.")
    elif 25 < risk_percentage <= 50:
        pdf.multi_cell(0, 10, txt="Risco moderado: O risco está em um nível intermediário. Monitoramento e ações preventivas são recomendadas.")
    elif 50 < risk_percentage <= 75:
        pdf.multi_cell(0, 10, txt="Risco alto: O risco está em um nível elevado. Ações corretivas e acompanhamento intensivo são necessários.")
    else:
        pdf.multi_cell(0, 10, txt="Risco muito alto: O risco está crítico e requer medidas imediatas e intensivas para mitigação.")

    # Salvar o PDF temporariamente
    temp_dir = tempfile.mkdtemp()
    pdf_output = os.path.join(temp_dir, f"{risk_analysis.replace(' ', '_')}_analise.pdf")
    pdf.output(pdf_output)

    return pdf_output

# Permitir que o usuário insira o título da aplicação
app_title = st.text_input('Título da aplicação', 'Avaliação de Risco - Perguntas e Pesos')

# Exibir o título inserido pelo usuário
st.title(app_title)

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
if st.button('Salvar Análise como PDF'):
    # Criar um DataFrame com as perguntas, respostas e pesos
    data = pd.DataFrame({
        'Pergunta': questions,
        'Resposta': responses,
        'Peso': weights
    })

    # Baixar a imagem de logo (se necessário)
    logo_url = "https://example.com/logo.png"  # Substitua pela URL da imagem
    logo_path = download_image(logo_url)

    # Gerar o PDF
    pdf_output = generate_pdf(data, risk_analysis, validated_by, risk_percentage, logo_path)

    # Fornecer link para download
    with open(pdf_output, "rb") as file:
        st.download_button(
            label="Baixar PDF",
            data=file,
            file_name=f"{risk_analysis}_analise.pdf",
            mime="application/pdf"
        )
