import requests
from fpdf import FPDF
import tempfile
import os
import streamlit as st

# Atualizar a função de gerar o PDF para usar o logo da URL fornecida
def generate_pdf(data, risk_analysis, validated_by, risk_percentage, logo_url):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Baixar a imagem do logo diretamente da URL fornecida
    if logo_url:
        response = requests.get(logo_url)
        if response.status_code == 200:
            # Salvar a imagem temporariamente
            logo_path = os.path.join(tempfile.mkdtemp(), "logo.png")
            with open(logo_path, "wb") as f:
                f.write(response.content)  # Salva a imagem
            pdf.image(logo_path, x=10, y=8, w=30)  # Ajuste a posição e o tamanho conforme necessário

    # Continue com o restante do código do PDF (sem alterações)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Análise de Risco: {risk_analysis}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Validado por: {validated_by}", ln=True)
    pdf.ln(10)

    # Tabela de dados
    pdf.set_font("Arial", '', 10)
    pdf.cell(40, 10, 'Pergunta', border=1, align='C')
    pdf.cell(40, 10, 'Resposta', border=1, align='C')
    pdf.cell(40, 10, 'Peso', border=1, align='C')
    pdf.ln()

    for question, response, weight in zip(data['Pergunta'], data['Resposta'], data['Peso']):
        pdf.cell(40, 10, question, border=1)
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

# Título da aplicação
st.title('Avaliação de Risco - Perguntas e Pesos')

# Definir a URL do logo que você forneceu
logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnwWi_O_IdR0kx6Txms27FANejY4FFxZbUjw&s"

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

    # Gerar o PDF com o logo da URL fornecida
    pdf_file = generate_pdf(data, risk_analysis, validated_by, risk_percentage, logo_url)

    # Fornecer o link para download
    st.success(f'Análise salva com sucesso como PDF!')
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Clique para baixar o PDF",
            data=f.read(),
            file_name=os.path.basename(pdf_file),
            mime="application/pdf"
        )
