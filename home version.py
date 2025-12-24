#!/usr/bin/env python3.11
# coding=utf-8

"""
tested in Python 3.11
"""
import csv, pygame, sys, os, serial
from pygame.locals import FULLSCREEN, USEREVENT, KEYUP, K_SPACE, K_RETURN, K_ESCAPE, QUIT, Color, K_c, K_b, K_m, K_p
from os.path import isfile, join
from random import randint, shuffle
from time import gmtime, strftime

from pathlib import Path

script_path = Path(__file__).parent.resolve()

debug_mode = False # Modo de depuración (True/False)

class TextRectException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message

# Configurations:
FullScreenShow = True  # Pantalla completa automáticamente al iniciar el experimento
test_name = "Facial Detection Task"
date_name = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

answers_options = ["Neutral", "Happy", "Sad"]

# Se usará en la creación del ID para poder separar a los usuarios y darle orden a las alternativas
answers_options_order = {
    1: ["Neutral", "Happy", "Sad"],
    2: ["Happy", "Sad", "Neutral"],
    3: ["Sad", "Neutral", "Happy"],
    4: ["Neutral", "Sad", "Happy"],
    5: ["Happy", "Neutral", "Sad"],
    6: ["Sad", "Happy", "Neutral"]
}

# Image Loading
happy_images_list = [script_path/"media"/"images"/"Happy"/ f for f in os.listdir(
    script_path/"media"/"images"/"Happy") if isfile(join(script_path/"media"/"images"/"Happy", f))]
neutral_images_list = [script_path/"media"/"images"/"Neutral"/ f for f in os.listdir(
    script_path/"media"/"images"/"Neutral") if isfile(join(script_path/"media"/"images"/"Neutral", f))]
sad_images_list = [script_path/"media"/"images"/"Sad"/ f for f in os.listdir(
    script_path/"media"/"images"/"Sad") if isfile(join(script_path/"media"/"images"/"Sad", f))]

shuffle(happy_images_list)
shuffle(neutral_images_list)
shuffle(sad_images_list)

first_testing_image_list = happy_images_list[40:43] + neutral_images_list[40:43] + sad_images_list[40:43]
second_testing_image_list = happy_images_list[43:46] + neutral_images_list[43:46] + sad_images_list[43:46]
shuffle(first_testing_image_list)
shuffle(second_testing_image_list)

happy_images_list = happy_images_list[:40]
neutral_images_list = neutral_images_list[:40]
sad_images_list = sad_images_list[:40]

first_experiment_block = happy_images_list[:20] + neutral_images_list[:20] + sad_images_list[:20]

shuffle(first_experiment_block)

second_experiment_block = happy_images_list[20:40] + neutral_images_list[20:40] + sad_images_list[20:40]

shuffle(second_experiment_block)

base_size = 350

# Port address and triggers
lpt_address = 0xD100
trigger_latency = 5
start_trigger = 254
stop_trigger = 255

# Experiment Trigger list

# 100: Inicio experimento / instrucciones
# 101: Inicio bloque 1
# 102: Fin bloque 1 / inicio pausa
# 103: Inicio bloque 2
# 104: Fin experimento
# 200: Onset cruz de fijación
# 310: Onset cara Neutra
# 320: Onset cara Feliz
# 330: Onset cara Triste
# 399: Offset cara (desaparición)
# 400: Onset pantalla de pregunta
# 501: Tecla presionada: "Triste"
# 502: Tecla presionada: "Neutra"
# 503: Tecla presionada: "Feliz"
# 600: Inicio ITI (Pantalla en blanco)

# 254: Start experiment
# 255: Stop experiment

trigger_helper = {
    "instruction": 100,
    "start_block_1": 101,
    "end_block_1": 102,
    "start_block_2": 103,
    "end_block_1": 104,
    "fixation_onset": 150,
    "neutral_face_onset": 160,
    "happy_face_onset": 170,
    "sad_face_onset": 180,
    "face_offset": 190, # = iti_onset
    "question_onset": 200,
    "answer_neutral": 210,
    "answer_happy": 220,
    "answer_sad": 230
}

# Onscreen instructions
def select_slide(slide_name, variables=None, answers_options = ["Neutral", "Happy", "Sad"]):

    if variables is None:
        variables = {"block_number": 0, "practice": True}

    # translate the answer list
    answer_dictionary = {"Neutral": "Neutra", "Happy": "Feliz", "Sad": "Triste"}
    variables["answers_options_spanish"] = [answer_dictionary[ans] for ans in answers_options]

    basic_slides = {
        'welcome': [
            u"Bienvenido/a, a este experimento!!!",
            " ",
            u"Se te indicará paso a paso que hacer."
        ],
        'Practice_1': [
            u"Empezaremos con una práctica para familiarizarnos con la tarea.",
            " ",
            u"Luego de ver un rostro deberás categorizar su expresión emocional lo más rápido y preciso posible.",
            " ",
            u"Para este bloque tendrás que responder con la mano "+ ("derecha." if variables.get("hand", "R") == "R" else "izquierda."),
        ],
        'Practice_2': [
            u"Ahora haremos una segunda práctica.",
            " ",
            u"Recuerda que luego de ver un rostro deberás categorizar su expresión emocional lo más rápido y preciso posible.",
            " ",
            u"Para este bloque tendrás que responder con la mano "+ ("derecha." if variables.get("hand", "R") == "R" else "izquierda."),
        ],
        'intro_block': [
            u"Ahora comenzaremos con el experimento.",
            " ",
            u"Se le presentará una secuencia de caras con diferentes expresiones emocionales.",
            u"Su tarea es categorizar la emoción de cada cara lo más rápido y preciso posible.",
            " ",
            u"Para este bloque tendrás que responder con la mano "+ ("derecha." if variables.get("hand", "R") == "R" else "izquierda."),
        ],
        'Question': [
            u"C: " + variables["answers_options_spanish"][0] + "      B: " + variables["answers_options_spanish"][1] + "      M: " + variables["answers_options_spanish"][2]
        ],
        'Break': [
            u"Puedes tomar un descanso.",
            " ",
            u"Para el siguiente bloque tendrás que responder con la mano contraria.",
            " ",
            u"En este bloque deberás responder con la mano "+ ("derecha." if variables.get("hand", "R") == "R" else "izquierda."),
            " ",
            u"Cuando te sientas listo para continuar presiona Espacio."
        ],
        'farewell': [
            u"El experimento ha terminado.",
            "",
            u"Muchas gracias por su colaboración!!"
        ]
    }

    return (basic_slides[slide_name])


# EEG Functions
def init_lpt(address):
    """Creates and tests a parallell port"""
    try:
        from ctypes import windll
        global io
        io = windll.dlportio  # requires dlportio.dll !!!
        print('Parallel port opened')
    except:
        pass
        print("Oops!", sys.exc_info(), "occurred.")
        print('The parallel port couldn\'t be opened')
    try:
        io.DlPortWritePortUchar(address, 0)
        print('Parallel port set to zero')
    except:
        pass
        print('Failed to send initial zero trigger!')


def send_trigger(trigger, address, latency):
    """Sends a trigger to the parallell port"""
    try:
        io.DlPortWritePortUchar(address, trigger)  # Send trigger
        pygame.time.delay(latency)  # Keep trigger pulse for some ms
        io.DlPortWritePortUchar(address, 0)  # Get back to zero after some ms
        print('Trigger ' + str(trigger) + ' sent')
    except:
        pass
        print('Failed to send trigger ' + str(trigger))


def init_com(address="COM3"):
    """Creates and tests a serial port"""
    global ser
    try:
        ser = serial.Serial()
        ser.port = address
        ser.baudrate = 115200
        ser.open()
        print('Serial port opened')
    except:
        pass
        print('The serial port couldn\'t be opened')


def send_triggert(trigger):
    """Sends a trigger to the serial port"""
    try:
        ser.write((trigger).to_bytes(1, 'little'))
        print('Trigger ' + str(trigger) + ' sent')
    except:
        pass
        print('Failed to send trigger ' + str(trigger))


def sleepy_trigger(trigger, latency=100):
    send_triggert(trigger)
    pygame.time.wait(latency)


def close_com():
    """Closes the serial port"""
    try:
        ser.close()
        print('Serial port closed')
    except:
        pass
        print('The serial port couldn\'t be closed')


# Text Functions
def setfonts():
    """Sets font parameters"""
    global bigchar, char, charnext
    pygame.font.init()
    font = join('media', 'Arial_Rounded_MT_Bold.ttf')
    bigchar = pygame.font.Font(script_path/font, 96)
    char = pygame.font.Font(script_path/font, 32)
    charnext = pygame.font.Font(script_path/font, 24)


def paragraph(text, key=None, no_foot=False, color=None, limit_time=0, row=None, is_clean=True):
    """Organizes a text into a paragraph"""
    if is_clean:
        screen.fill(background)

    if row == None:
        row = center[1] - 20 * len(text)

    if color == None:
        color = char_color

    for line in text:
        phrase = char.render(line, True, color)
        phrasebox = phrase.get_rect(centerx=center[0], top=row)
        screen.blit(phrase, phrasebox)
        row += 40
    if key != None:
        if key == K_SPACE:
            foot = u"Para continuar presione la tecla Espacio..."
        elif key == K_RETURN:
            foot = u"Para continuar presione la tecla ENTER..."
    else:
        foot = u"Responda con la fila superior de teclas de numéricas"
    if no_foot:
        foot = ""
    nextpage = charnext.render(foot, True, charnext_color)
    nextbox = nextpage.get_rect(left=15, bottom=resolution[1] - 15)
    screen.blit(nextpage, nextbox)
    pygame.display.flip()

    if key != None or limit_time != 0:
        wait(key, limit_time)


# Program Functions
def init():
    """Init display and others"""
    setfonts()
    global screen, resolution, center, background, char_color, charnext_color, fix, fixbox
    pygame.init()  # soluciona el error de inicializacion de pygame.time
    pygame.display.init()
    pygame.display.set_caption(test_name)
    pygame.mouse.set_visible(False)
    if FullScreenShow:
        resolution = (pygame.display.Info().current_w,
                      pygame.display.Info().current_h)
        screen = pygame.display.set_mode(resolution, FULLSCREEN)
    else:
        try:
            resolution = pygame.display.list_modes()[3]
        except:
            resolution = (1280, 720)
        screen = pygame.display.set_mode(resolution)
    center = (int(resolution[0] / 2), int(resolution[1] / 2))
    background = Color('white')
    char_color = Color('black')
    charnext_color = Color('black')
    fix = char.render('+', True, char_color)
    fixbox = fix.get_rect(centerx=center[0], centery=center[1])
    screen.fill(background)
    pygame.display.flip()


def blackscreen(blacktime=0):
    """Erases the screen"""
    screen.fill(background)
    pygame.display.flip()
    pygame.time.delay(blacktime)


def ends():
    """Closes the show"""
    blackscreen()
    dot = char.render('.', True, char_color)
    dotbox = dot.get_rect(left=15, bottom=resolution[1] - 15)
    screen.blit(dot, dotbox)
    pygame.display.flip()
    while True:
        for evento in pygame.event.get():
            if evento.type == KEYUP and evento.key == K_ESCAPE:
                pygame_exit()


def pygame_exit():
    pygame.quit()
    sys.exit()


def wait(key, limit_time):
    """Hold a bit"""

    TIME_OUT_WAIT = USEREVENT + 1
    if limit_time != 0:
        pygame.time.set_timer(TIME_OUT_WAIT, limit_time, loops=1)

    tw = pygame.time.get_ticks()

    switch = True
    while switch:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame_exit()
            elif event.type == KEYUP:
                if event.key == key:
                    switch = False
            elif event.type == TIME_OUT_WAIT and limit_time != 0:
                switch = False

    pygame.time.set_timer(TIME_OUT_WAIT, 0)
    pygame.event.clear()                    # CLEAR EVENTS

    return (pygame.time.get_ticks() - tw)


def image_in_center(picture, xdesv=0, ydesv=0):
    center = [int(resolution[0] / 2) + xdesv, int(resolution[1] / 2) + ydesv]
    return [x - picture.get_size()[count]/2 for count, x in enumerate(center)]


def show_image(image, scale, grayscale=False):
    screen.fill(background)
    try:
        picture = pygame.image.load(image)
    except pygame.error as e:
        print(f"Error al cargar imagen {image}: {e}") if debug_mode else None
        return

    image_real_size = picture.get_size()
    percentage = scale / image_real_size[0]
    picture = pygame.transform.scale(picture, [int(scale), int(image_real_size[1]*percentage)])

    # Convertir a blanco y negro si se requiere
    if grayscale:
        width, height = picture.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = picture.get_at((x, y))
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                picture.set_at((x, y), (gray, gray, gray, a))

    screen.blit(picture, image_in_center(picture, ydesv=-int(resolution[1] / 16) ))

    pygame.display.flip()


def wait_answer(image, testing = False, answers_options = ["Neutral", "Happy", "Sad"]):
    tw = pygame.time.get_ticks()
    done = False
    selected_answer = None
    is_correct = None

    paragraph(select_slide('Question', answers_options=answers_options), key=None, no_foot=True, row=center[1] + resolution[1]*3/16, is_clean=False)

    while not done:
        for event in pygame.event.get():

            if event.type == KEYUP and event.key == K_ESCAPE and debug_mode:
                pygame_exit()

            elif event.type == KEYUP and event.key == K_c:
                selected_answer = answers_options[0]
                done = True

            elif event.type == KEYUP and event.key == K_b:
                selected_answer = answers_options[1]
                done = True

            elif event.type == KEYUP and event.key == K_m:
                selected_answer = answers_options[2]
                done = True

    rt = pygame.time.get_ticks() - tw

    sleepy_trigger(210 + (10 if selected_answer == "Happy" else 0) + (20 if selected_answer == "Sad" else 0), lpt_address, trigger_latency) # user answer trigger

    # Se obtiene el path relativo de la imagen
    relative_path = Path(image).relative_to(script_path)

    # Se divide el path relativo para obtener las carpetas que contienen la imagen
    if (len(relative_path.parts) >= 3 and not testing):
        image_type = relative_path.parts[2]
        print(image_type) if debug_mode else None
        print(selected_answer) if debug_mode else None

        is_correct = selected_answer == image_type

        print(is_correct) if debug_mode else None

        #print(252 + (0 if image_type == "B" else 1)) if debug_mode else None
        # sleepy_trigger(252 + (0 if image_type == "B" else 1) , lpt_address, trigger_latency) # user answer

    pygame.event.clear()                    # CLEAR EVENTS
    return ({"rt": rt, "is_correct": is_correct, "selected_answer": selected_answer})


def show_images(image_list, practice=False, uid=None, dfile=None, block=None, block_answers_order = ["Neutral", "Happy", "Sad"]):
    phase_change = USEREVENT + 5
    pygame.time.set_timer(phase_change, 500, loops=1)

    done = False
    count = 0

    screen.fill(background)
    pygame.display.flip()

    answers_list = []

    actual_phase = 1

    while not done:
        for event in pygame.event.get():
            if event.type == KEYUP and event.key == K_ESCAPE and debug_mode:
                pygame_exit()

            elif event.type == KEYUP and event.key == K_p and debug_mode:
                done = True

            elif event.type == phase_change:
                if actual_phase == 1:
                    screen.fill(background)
                    screen.blit(fix, fixbox)
                    pygame.display.update(fixbox)
                    pygame.display.flip()
                    sleepy_trigger(150, lpt_address, trigger_latency) # fixation
                    pygame.time.set_timer(phase_change, 1000, loops=1)
                    actual_phase = 2
                elif actual_phase == 2:
                    show_image(image_list[count], base_size, grayscale=True)

                    relative_path = Path(image).relative_to(script_path)
                    image_type = relative_path.parts[2]
                    sleepy_trigger(160 + (10 if image_type == "Happy" else 0) + (20 if image_type == "Sad" else 0), lpt_address, trigger_latency) # image type trigger

                    pygame.time.set_timer(phase_change, 200, loops=1)
                    actual_phase = 3
                elif actual_phase == 3:

                    sleepy_trigger(200, lpt_address, trigger_latency) # question onset trigger
                    answer = wait_answer(image_list[count], practice, block_answers_order)
                    answers_list.append([image_list[count], answer, block_answers_order[:]]) # Se usa [:] para copiar la lista y no referenciarla
                    count += 1
                    if count >= len(image_list):
                        done = True

                    screen.fill(background)
                    pygame.display.flip()
                    sleepy_trigger(190, lpt_address, trigger_latency) # image offset trigger

                    pygame.time.set_timer(phase_change, randint(1000, 1200), loops=1)
                    actual_phase = 1

    pygame.time.set_timer(phase_change, 0)

    pygame.event.clear()                    # CLEAR EVENTS

    # acá se almacenará la answers_list en el archivo dfile
    if dfile is not None:
        for answer in answers_list:
            # Unir la lista con guiones en lugar de comas
            answers_order = "-".join(answer[2])  # "Neutral-Happy-Sad"
            dfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (uid,
                                                 answer[0].split('\\')[-1].split('.')[0],
                                                    block,
                                                    answer[1]['rt'],
                                                    answer[0].split('\\')[2],
                                                    answers_order,
                                                    answer[1]['selected_answer'],
                                                    int(answer[1]['is_correct']) if answer[1]['is_correct'] is not None else ""
                                                 ))
        dfile.flush()
    else:
        print("Error al cargar el archivo de datos")

# Main Function
def main():
    """Game's main loop"""

    init_com()

    # Si no existe la carpeta data se crea
    if not os.path.exists(script_path/'data/'):
        os.makedirs(script_path/'data/')

    # Username = id_condition_hand_answersOrder
    # condition = control or experimental, hand = L or R, answersOrder = 2 digits from 1 to 6
    # example: 4321_E_R_12

    correct_sub_name = False
    first_round = True

    while not correct_sub_name:
        os.system('cls')
        if not first_round:
            print("ID ingresado no cumple con las condiciones, contacte con el encargado...")

        first_round = False
        subj_name = input(
            "Ingrese el ID del participante y presione ENTER para iniciar: ")

        if not subj_name or subj_name.strip() == "" or len(subj_name.split("_")) != 4:
            continue

        uid = subj_name.split("_")[0].strip()
        condition = subj_name.split("_")[1].strip()
        firsthand = subj_name.split("_")[2].strip()
        secondhand = "L" if firsthand == "R" else "R"
        answers_order_1 = int(subj_name.split("_")[3].strip()[0])
        answers_order_2 = int(subj_name.split("_")[3].strip()[1])

        if condition in ["C", "E"] and firsthand in ["L", "R"] and answers_order_1 in range(1,7) and answers_order_2 in range(1,7):
            correct_sub_name = True

    print("Condición seleccionada: " + condition) if debug_mode else None
    print("Mano de respuestas inicial: " + firsthand) if debug_mode else None
    print("Orden de respuestas bloque 1: " + ",".join(answers_options_order[answers_order_1])) if debug_mode else None
    print("Orden de respuestas bloque 2: " + ",".join(answers_options_order[answers_order_2])) if debug_mode else None

    csv_name = date_name + '_' + subj_name + '.csv'
    dfile = open(script_path/"data"/csv_name, 'w')
    dfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % ("Sujeto", "IdImagen", "Bloque", "TReaccion", "TipoImagen", "OrdenRespuestas", "Respuesta", "Acierto"))
    dfile.flush()

    init()

    send_triggert(start_trigger)

    paragraph(select_slide('welcome'), key = K_SPACE)

    # ------------------------ Practice block ------------------------
    paragraph(select_slide('Practice_1', variables={
          "block_number": 0, "practice": True, "hand": firsthand}), key = K_SPACE)

    # Para la práctica se usará un orden de respuestas que no esté en la variable de answers_order_1 o answers_order_2
    numbers_list = [1, 2, 3, 4, 5, 6]

    # Remover los números ya usados
    numbers_list.remove(answers_order_1)
    numbers_list.remove(answers_order_2)

    numero_aleatorio = randint(0, len(numbers_list)-1)
    numero_aleatorio = numbers_list[numero_aleatorio]

    if debug_mode:
        show_images(first_testing_image_list, practice = False, uid=uid, dfile=dfile, block=0, block_answers_order = answers_options_order[numero_aleatorio])
    else:
        show_images(first_testing_image_list, practice = True)

    paragraph(select_slide('Practice_2', variables={
          "block_number": 0, "practice": True, "hand": secondhand}), key = K_SPACE)

    numbers_list.remove(numero_aleatorio)
    numero_aleatorio = randint(0, len(numbers_list)-1)
    numero_aleatorio = numbers_list[numero_aleatorio]

    if debug_mode:
        show_images(second_testing_image_list, practice = False, uid=uid, dfile=dfile, block=0, block_answers_order = answers_options_order[numero_aleatorio])
    else:
        show_images(second_testing_image_list, practice = True)

    # ------------------------ first block ------------------------

    sleepy_trigger(100, lpt_address, trigger_latency) # instructions
    paragraph(select_slide('intro_block', variables= {"hand": firsthand}), key = K_SPACE)

    sleepy_trigger(101, lpt_address, trigger_latency) # start block 1
    show_images(first_experiment_block, practice = False, uid=uid, dfile=dfile, block=1, block_answers_order = answers_options_order[answers_order_1])
    sleepy_trigger(102, lpt_address, trigger_latency) # end block 1
    # sleepy_trigger(240 + 1, lpt_address, trigger_latency) # block number

    sleepy_trigger(100, lpt_address, trigger_latency) # instructions
    paragraph(select_slide('Break', variables= {"hand": secondhand}), key = K_SPACE, no_foot = True)
    sleepy_trigger(103, lpt_address, trigger_latency) # start block 2
    show_images(second_experiment_block, practice = False, uid=uid, dfile=dfile, block=2, block_answers_order = answers_options_order[answers_order_2])
    sleepy_trigger(104, lpt_address, trigger_latency) # end block 2
    # sleepy_trigger(240 + 1, lpt_address, trigger_latency) # block number

    paragraph(select_slide('farewell'), key = K_SPACE, no_foot = True)
    send_triggert(stop_trigger)
    dfile.close()

    close_com()
    ends()


# Experiment starts here...
if __name__ == "__main__":
    main()
