from moviepy.editor import *

def aumentar_qualidade_video(input_file, output_file):
    # Carregar o vídeo
    video = VideoFileClip(input_file)

    # Aumentar a qualidade do vídeo para 1080p
    video_1080p = video.resize((1920, 1080))

    # Salvar o vídeo com a nova qualidade
    video_1080p.write_videofile(output_file)

# Exemplo de uso
input_file = r'C:\Users\Léo\Downloads\videoplayback (1).mp4'
output_file = r'C:\Users\Léo\Downloads\VIDEO\saida_1080p.mp4'
aumentar_qualidade_video(input_file, output_file)