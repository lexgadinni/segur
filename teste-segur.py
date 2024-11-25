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

# Função para gerar o PDF com os dados
def generate_pdf(data, risk_analysis, validated_by, risk_percentage, logo_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Adicionar o logo
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=30)  # Ajuste a posição e o tamanho do logo conforme necessário
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Análise de Risco: {risk_analysis}", ln=True, align='C')

    pdf.ln(10)  # Linha em branco

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Validado por: {validated_by}", ln=True)

    pdf.ln(10)  # Linha em branco

    # Tabela de dados
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 10, 'Pergunta', border=1, align='C')  # Tamanho da célula ajustado
    pdf.cell(40, 10, 'Resposta', border=1, align='C')
    pdf.cell(40, 10, 'Peso', border=1, align='C')
    pdf.ln()

    # Ajuste da tabela para o conteúdo
    for question, response, weight in zip(data['Pergunta'], data['Resposta'], data['Peso']):
        pdf.multi_cell(80, 10, question, border=1)  # Usar multi_cell para ajustar o texto da pergunta
        pdf.set_xy(pdf.get_x() + 80, pdf.get_y() - 10)  # Mover o cursor para a próxima célula na linha
        pdf.cell(40, 10, response, border=1)
        pdf.cell(40, 10, str(weight), border=1)
        pdf.ln()

    # Adicionar o percentual de risco e a explicação
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

    # Salvar o arquivo PDF em um diretório temporário
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
    # Organizar os dados para gerar o PDF
    data = {
        'Análise de Risco': [risk_analysis] * len(questions),
        'Quem Validou': [validated_by] * len(questions),
        'Pergunta': questions,
        'Resposta': responses,
        'Peso': weights
    }

    # URL da imagem no GitHub
    image_url = "https://raw.githubusercontent.com/lexgadinni/segur/main/images.png"
    
    # Baixar a imagem do GitHub
    logo_path = download_image(image_url)
    
    # Gerar o PDF
    pdf_file = generate_pdf(data, risk_analysis, validated_by, risk_percentage, logo_path)

    # Fornecer o link para download
    st.success(f'Análise salva com sucesso como PDF!')
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Clique para baixar o PDF",
            data=f.read(),
            file_name=os.path.basename(pdf_file),
            mime="application/pdf"
        )
