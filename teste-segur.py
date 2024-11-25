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
