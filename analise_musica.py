try:
    from scipy.io import wavfile
    from scipy.signal import spectrogram, periodogram
    import sqlite3
    import numpy as np
    import os
    import matplotlib.pyplot as plt
    import subprocess
    import pandas as pd
except ImportError:
    print("Import Error")
    quit(1)

conn = sqlite3.connect("musicas.db")
cursor = conn.cursor()

def ler_musica(musica, formato):
    """Le os arquivos no formato mp3 e converter para wav mono channel"""

    subprocess.call(['ffmpeg', '-i', '%s%s' %(musica, formato),'-ac', '1','-ab', '320k','%s.wav' %musica])

def inicializa_tabela():
    """Inicializa o banco de dados caso não exista"""
    
    cursor.execute("CREATE TABLE IF NOT EXISTS musicas (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, musica TEXT, valor FLOAT)")

def inserir_dados(nova_musica, novo_valor):
    """Insere os dados passados no banco de dados"""
    
    cursor.execute("INSERT INTO musicas(musica, valor) VALUES(?, ?)", (nova_musica, float(novo_valor)))
    conn.commit()

def fechar_banco():
    """Termina a conexão com o banco de dados"""
    
    cursor.close()
    conn.close()

def plotar(spectogram, times, frequencies):
    """Plota o spectrograma da música"""

    spectogram = 10 * np.log10(spectogram)

    plt.pcolormesh(times, frequencies, spectogram)
    plt.show()

def analise_musica(musica):
    """Le o arquivo wav da musica e retira as informações"""

    sample_rate, samples = wavfile.read('%s.wav' %musica)

    frequencies, times, spectogram = spectrogram(samples, sample_rate)

    #f, pxx = periodogram(samples, sample_rate)

    return np.mean(spectogram)

def comparar_musica(spectogram1, spectogram2):
    """Compara o valor médio de 2 spectrogramas"""

    if spectogram1 >= spectogram2:
        return (spectogram2 * 100) / spectogram1
    elif spectogram1 < spectogram2:
        return (spectogram1 * 100) / spectogram2

def guardar_comparacoes(lista, nome_musica):
    """Guardas as recomendações em relação a uma música em um txt"""

    arquivo = open("Recomendacoes_%s.txt" %nome_musica, "w")
    if os.stat("Recomendacoes_%s.txt" %nome_musica).st_size == 0:
        arquivo.write("Melhores recomendações para a música %s\n" %nome_musica)
    for i in range(len(lista)):
        if lista[i][0] != nome_musica:
            arquivo.write("\n%s = %.2f" %(lista[i][0], lista[i][1]))

def ler_dados(valor_comparar, nome_musica):
    "Recebe o valor de uma música e compara com todas que estão no banco de dados"

    cursor.execute('SELECT * FROM musicas')
    valores = []
    for linha in cursor.fetchall():
        valor = comparar_musica(valor_comparar, linha[2])
        valores.append([linha[1], valor])
    valores.sort(key=lambda x: x[1], reverse=True)
    guardar_comparacoes(valores, nome_musica)

def imprimir_dados():
    cursor.execute('SELECT * FROM musicas')
    for linha in cursor.fetchall():
        print(linha)

def apagar_musicas():
    """Apaga as musicas de formato .wav na pasta atual"""

    for file in os.listdir(os.getcwd()):
        if (file.endswith(".wav")) or (file.endswith(".mp3")) or (file.endswith(".flac")):
            os.remove(file)

def criar_banco_musica():
    """Le todas as músicas na pasta atual e guarda o valor de cada uma"""

    for file in os.listdir(os.getcwd()):
        if (file.endswith(".mp3")) or (file.endswith(".flac")):
            nome_musica, formato_musica = os.path.splitext(os.path.basename(file))
            ler_musica(nome_musica, formato_musica)
            spec1 = analise_musica(nome_musica)
            inserir_dados(nome_musica, spec1)
    apagar_musicas()

def recomendar_musicas(musica):
    """Recebe uma música e busca no banco de dados as mais parecidas"""

    ler_musica(musica, ".mp3")
    spec1 = analise_musica(musica)
    ler_dados(spec1, musica)
    apagar_musicas()
