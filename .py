from rembg import remove
from PIL import Image
import io

# Carregar a imagem
input_path = 'input_image.png'  # Caminho da imagem original
output_path = 'output_image.png'  # Caminho para salvar a imagem sem fundo

# Abrir a imagem
with open(input_path, 'rb') as input_file:
    input_image = input_file.read()

# Remover o fundo
output_image = remove(input_image)

# Salvar a imagem sem fundo
with open(output_path, 'wb') as output_file:
    output_file.write(output_image)

print(f'Imagem salva em: {output_path}')
