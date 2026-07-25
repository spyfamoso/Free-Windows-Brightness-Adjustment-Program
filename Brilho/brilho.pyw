import tkinter as tk
import ctypes
import math
import pystray
from PIL import Image
import threading
import os
import sys
import winreg
import time


# ==========================
# CONFIGURAÇÕES
# ==========================

gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32

brilho_atual = 100
gama_atual = 1.0


# ==========================
# CAMINHOS
# ==========================

def caminho_recurso(nome):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(
            sys._MEIPASS,
            nome
        )

    return os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        nome
    )


PASTA_CONFIG = os.path.join(
    os.getenv("APPDATA"),
    "ControleBrilho"
)

ARQUIVO_CONFIG = os.path.join(
    PASTA_CONFIG,
    "config.txt"
)


# ==========================
# INICIAR COM WINDOWS
# ==========================

def adicionar_inicio_windows():

    try:

        caminho_exe = os.path.abspath(
            sys.argv[0]
        )

        chave = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(
            chave,
            "ControleBrilho",
            0,
            winreg.REG_SZ,
            caminho_exe
        )

        winreg.CloseKey(chave)

    except Exception:
        pass



# ==========================
# CONFIGURAÇÃO
# ==========================

def carregar_config():

    global brilho_atual, gama_atual

    if os.path.exists(ARQUIVO_CONFIG):

        try:

            with open(
                ARQUIVO_CONFIG,
                "r"
            ) as arquivo:

                linhas = arquivo.readlines()

                brilho_atual = int(
                    linhas[0].split("=")[1]
                )

                gama_atual = float(
                    linhas[1].split("=")[1]
                )

        except:

            brilho_atual = 100
            gama_atual = 1.0



def salvar_config():

    os.makedirs(
        PASTA_CONFIG,
        exist_ok=True
    )

    with open(
        ARQUIVO_CONFIG,
        "w"
    ) as arquivo:

        arquivo.write(
            f"brilho={brilho_atual}\n"
        )

        arquivo.write(
            f"gama={gama_atual}\n"
        )



# ==========================
# APLICAR NA TELA
# ==========================

def aplicar_configuracao():

    global brilho_atual, gama_atual


    hdc = user32.GetDC(None)


    ramp = (
        ctypes.c_ushort * (3 * 256)
    )()


    for i in range(256):

        valor = i / 255.0


        valor = math.pow(
            valor,
            1 / gama_atual
        )


        valor *= (
            brilho_atual / 100
        )


        valor = max(
            0,
            min(1, valor)
        )


        cor = int(
            valor * 65535
        )


        ramp[i] = cor
        ramp[i + 256] = cor
        ramp[i + 512] = cor



    gdi32.SetDeviceGammaRamp(
        hdc,
        ctypes.byref(ramp)
    )

# ==========================
# CONTROLES
# ==========================

def mudar_brilho(valor):

    global brilho_atual

    brilho_atual = int(valor)

    salvar_config()
    aplicar_configuracao()



def mudar_gama(valor):

    global gama_atual

    gama_atual = float(valor)

    salvar_config()
    aplicar_configuracao()



def restaurar():

    global brilho_atual, gama_atual

    brilho_atual = 100
    gama_atual = 1.0


    slider_brilho.set(
        brilho_atual
    )

    slider_gama.set(
        gama_atual
    )


    salvar_config()
    aplicar_configuracao()



# ==========================
# MANTER EFEITO NO JOGO
# ==========================

def manter_brilho():

    while True:

        try:
            aplicar_configuracao()

        except Exception:
            pass


        # reaplica a cada 0.2 segundos
        time.sleep(0.2)



# ==========================
# INTERFACE
# ==========================

janela = tk.Tk()

janela.title(
    "Controle de Tela"
)

janela.geometry(
    "350x230"
)



def mostrar():

    janela.after(
        0,
        janela.deiconify
    )



def esconder():

    janela.withdraw()



janela.protocol(
    "WM_DELETE_WINDOW",
    esconder
)



tk.Label(
    janela,
    text="Controle de imagem",
    font=("Arial", 12)
).pack(pady=10)



tk.Label(
    janela,
    text="Brilho"
).pack()



slider_brilho = tk.Scale(
    janela,
    from_=10,
    to=100,
    orient="horizontal",
    length=300,
    command=mudar_brilho
)

slider_brilho.pack()



tk.Label(
    janela,
    text="Gama"
).pack()



slider_gama = tk.Scale(
    janela,
    from_=0.5,
    to=2.5,
    resolution=0.1,
    orient="horizontal",
    length=300,
    command=mudar_gama
)

slider_gama.pack()



tk.Button(
    janela,
    text="Restaurar padrão",
    command=restaurar
).pack(pady=10)

# ==========================
# BANDEJA
# ==========================

def sair():

    try:
        restaurar_tela()
    except:
        pass


    try:
        icone.stop()
    except:
        pass


    janela.destroy()



def criar_menu():

    return pystray.Menu(

        pystray.MenuItem(
            "Abrir controle",
            mostrar
        ),


        pystray.MenuItem(
            "Sair",
            sair
        )

    )



def iniciar_bandeja():

    global icone


    imagem = Image.open(
        caminho_recurso(
            "icone.png"
        )
    )


    icone = pystray.Icon(
        "ControleBrilho",
        imagem,
        "Controle de Tela",
        criar_menu()
    )


    icone.run()



# ==========================
# INICIALIZAÇÃO
# ==========================

adicionar_inicio_windows()

carregar_config()


slider_brilho.set(
    brilho_atual
)


slider_gama.set(
    gama_atual
)


aplicar_configuracao()



# Mantém brilho/gama funcionando em jogos

threading.Thread(
    target=manter_brilho,
    daemon=True
).start()



# Ícone na bandeja

threading.Thread(
    target=iniciar_bandeja,
    daemon=True
).start()



janela.withdraw()



janela.mainloop()