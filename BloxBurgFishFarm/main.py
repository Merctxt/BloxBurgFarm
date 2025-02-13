import random
import time
from pynput.keyboard import Controller, Key
from mss import mss
import cv2
import numpy as np
import os

class Rod:
    def __init__(self):
        print("Rod initialized")
        self.keyboard = Controller()

    def catch(self):
        print("Fish detected! Pressing Enter to catch...")
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        time.sleep(random.uniform(0.3, 0.5))  # Delay para evitar repetições rápidas

    def cast(self):
        print("Casting the rod...")
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        time.sleep(random.uniform(0.3, 0.5))  # Delay entre ações

# Configuração da área de captura
bbox = (1250, 700, 1750, 950)  # Ajustado para Full HD

# Inicializar objetos
rod = Rod()
sct = mss()

# Configurar filtro de ruído
kernel_size = (3, 3)
kernel_el = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

# Variável para verificar o estado
was_submerged = False
ready_to_cast = True  # Controla se o script deve lançar a isca novamente

while True:
    last_detection = time.time()
    # Capturar a tela na área definida
    screen = np.array(sct.grab(bbox))

    # Mostrar a captura de tela original na janela
    cv2.imshow("Program's Vision", cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
    cv2.setWindowProperty("Program's Vision", cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow("Program's Vision", 50, 50)

    # Processar a imagem para detectar áreas brancas
    binary = np.zeros((screen.shape[:-1]))
    mask = np.logical_and(screen[:, :, 0] == screen[:, :, 1], screen[:, :, 1] == screen[:, :, 2])
    binary[mask] = 1

    # Aplicar filtro de ruído
    binary = cv2.erode(binary, kernel_el, (-1, -1))

    # Mostrar a janela binária processada
    cv2.imshow("Binary Vision", binary)
    cv2.setWindowProperty("Binary Vision", cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow("Binary Vision", 800, 50)

    # Calcular média da imagem processada
    average = np.average(binary)

    # Verificar se a isca está submersa
    is_submerged = average == 0

    if is_submerged and not was_submerged:
        # Se o peixe foi pego, pressione Enter para capturá-lo
        rod.catch()
        last_detection = time.time()
        # Preparar para lançar a isca novamente
        time.sleep(random.uniform(1.7, 2))  # Delay para evitar repetições rápidas
        rod.cast()
    else:
        if time.time() - last_detection > 20:
            rod.cast()
            last_detection = time.time()


    # Atualizar estado anterior
    was_submerged = is_submerged

    # Aguardar 25ms para exibição e permitir fechamento com 'q'
    if cv2.waitKey(25) & 0xFF == ord('q'):
        print("Exiting program...")
        break  # Encerra o loop principal

# Fechar janelas do OpenCV ao sair
cv2.destroyAllWindows()

# Forçar a saída completa do programa
os._exit(0)
