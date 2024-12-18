import pdfplumber
import pandas as pd
import re

def verify_date(string):
    # Padrões de data
    padroes_data = [
        r'\d{4}-\d{2}-\d{2}',  # Formato YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',   # Formato DD/MM/YYYY
        r'\d{2}-\d{2}-\d{4}',   # Formato DD-MM-YYYY
        r'\d{2}\.\d{2}\.\d{4}', # Formato DD.MM.YYYY
    ]

    for padrao in padroes_data:
        if re.match(padrao, string):
            return True
    return False

# Defina as configurações da tabela
settings = {
    "vertical_strategy": "explicit", 
    "horizontal_strategy": "text",
    "snap_y_tolerance": 4,
    "explicit_vertical_lines": [ 40, 90, 250, 310, 400, 490, 570 ],
}

def extract_tables_from_all_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []  # Lista para armazenar todas as tabelas
        
        for index, page in enumerate(pdf.pages):
            text = page.extract_text(keep_blank_chars=True)
            pattern = r"Agência | Conta"

            # Usando re.search() para verificar se o padrão está presente no texto
            header_page = re.search(pattern, text)

            crop_header_position = 220 if header_page else 80
            crop_box = (0, crop_header_position, page.width, page.height)

            # Recorte a página
            cropped_page = page.crop(crop_box)
            table = cropped_page.extract_table(settings)
            if table:
                # Remova linhas vazias
                table = [row for row in table if any(cell.strip() for cell in row)]
                all_tables.append(table)  # Adicione a tabela à lista de todas as tabelas
            else:
                print(f"Nenhuma tabela encontrada na página.")
        return all_tables  # Retorne a lista de todas as tabelas


def extract_ocr(table):
    # tables = extract_tables_from_all_pages(file)  # Substitua 'seu_arquivo.pdf' pelo caminho do seu arquivo e 0 pelo número da página
    # table = []

    # # Itera sobre cada sub-lista no array
    # for sublist in tables:
    #     # Usando extend() para adicionar os elementos de sublist a unified_list
    #     table.extend(sublist)

    if table is not None:
        date = ""
        allowed = True

        new_table = []
        for index, row in enumerate(table):
            numcolums_now = 0
            numcolums = 0
            col = ""
            for column in row:
                if column != "":
                    numcolums_now = numcolums_now + 1
            
            next_row = ""
            if index < len(table) - 1:
                next_row = table[index + 1]

                for column in next_row:
                    if column != "":
                        col = column
                        numcolums = numcolums + 1

            #Unir lançamentos que estão em 3 linhas
            if index > 2:
                prev_row = table[index - 1]
                cleaned_prev_row = [item for item in prev_row if item]
                
                prev_two_row = table[index - 2]

                #Verificar se a linha anterior há apenas 1 coluna preenchida
                if len(cleaned_prev_row) == 2:
                    #Verificar se a linha anterior está presente no lançamento 2 anteriores
                    if not prev_row[1] in prev_two_row[1]:
                        row[1] = prev_row[1] + " " + row[1]
            
            if numcolums == 1 and not "TRANSF" in next_row[1]:
                row[1] = row[1] + " " + col
        
            if row[0] != "":
                date = row[0]
            else:
                row[0] = date
            
            pattern_start = r"Últimos"
            pattern_end = r"Total"

            # Usando re.search() para verificar se o padrão está presente no texto
            if re.search(pattern_start, row[0]):
                allowed = False
                continue

            if not allowed and re.search(pattern_end, row[0]):
                allowed = True
                continue

            pattern_date = r"\d{2}/\d{2}/\d{4}"
            if numcolums_now > 1 and allowed and re.match(pattern_date, row[0]):
                new_table.append(row)

        for index, row in enumerate(new_table):
             print(row)
    return new_table

def normalizar_string(s):
    return s.replace(" ", "").lower()

def float_to_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def somar_valores_por_descricao(matriz, nomenclaturas):
    soma = 0
    for linha in matriz:
        if len(linha) >= 2:  # Verifica se a linha tem pelo menos 3 elementos
            descricao = linha[1]
            valor = ""  # Define um valor inicial para valor
            
            pattern = r'^\d+\.\d{2}$'

            if linha[3].replace(" ", "") != "":
                valor = linha[3]
            elif linha[4].replace(" ", "")  != "":
                valor = linha[4]
            
            # Corrigindo a formatação do valor
            valor = valor.replace('.', '').replace(',', '.').replace("-", "")  # Substitui '.' por '' e ',' por '.'
            try:
                # print(len(linha), index, linha[1], re.match(pattern, valor))
                if re.match(pattern, valor):
                    valor_float = float(valor)  # Converte para float

                    for nomenclatura in nomenclaturas:
                        new_nomenclature = nomenclatura.replace(" ", "")
                        pattern_description = rf"{new_nomenclature}"
                        match = re.search(pattern_description, descricao.replace(" ", ""), re.IGNORECASE)
                        
                        if match:  # Verifica se alguma nomenclatura está contida na descrição
                            soma += valor_float
            except ValueError:
                pass  # Ignora se não puder converter para float
    return float_to_brl(soma)

pdf_path = r"C:\Users\Léo\Downloads\L._DE_MORAES_MENESES_(BRADESCO_-_77015-9)-409627b7ff15 (1).pdf"

# Caminho para o arquivo Excel de saída
output_file = r"C:\Users\Léo\Downloads\tabelas_extraidas.xlsx"

# Extrair tabelas do PDF
tables = extract_tables_from_all_pages(pdf_path)

# Extrair dados da OCR
table = []
for sublist in tables:
    table.extend(sublist)

new_table = extract_ocr(table)

# Criar um DataFrame
df = pd.DataFrame(new_table)

# Salvar no Excel
df.to_excel(output_file, index=False)
print(f"Dados exportados com sucesso para {output_file}")