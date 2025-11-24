# Facial Detection Experiment

Experimento de detección y categorización de expresiones emocionales faciales utilizando pygame.

## Descripción

Este experimento presenta estímulos visuales de rostros con diferentes expresiones emocionales (Neutral, Feliz, Triste) que los participantes deben categorizar lo más rápido y preciso posible. El experimento está diseñado para investigación en psicología cognitiva y neurociencias.

## Requisitos del Sistema

- **Sistema Operativo:** Windows
- **Python:** 3.11 o superior
- **Dependencias:** Ver [requirements.txt](requirements.txt)

## Instalación

### 1. Instalar Python

Si no tiene Python instalado, descárguelo desde:
https://www.python.org/downloads/

**Importante:** Durante la instalación, asegúrese de marcar la opción "Add Python to PATH".

### 2. Instalar pip

Descargue el instalador de pip desde:
https://bootstrap.pypa.io/get-pip.py

Si no se descarga automáticamente, presione `CTRL + S` para guardarlo.

Para instalarlo:
1. Abra la carpeta donde descargó el archivo
2. Presione `Shift` + clic derecho en un espacio vacío
3. Seleccione "Abrir ventana de PowerShell aquí"
4. Ejecute: `python get-pip.py`

### 3. Instalar Dependencias

En la carpeta del proyecto, abra PowerShell y ejecute:

```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
Facial Detection/
├── home version.py          # Script principal del experimento
├── requirements.txt         # Dependencias de Python
├── README.md               # Este archivo
├── data/                   # Carpeta de datos de salida (se crea automáticamente)
├── media/
│   ├── images/
│   │   ├── Happy/         # Imágenes de rostros felices
│   │   ├── Neutral/       # Imágenes de rostros neutrales
│   │   └── Sad/           # Imágenes de rostros tristes
│   └── Arial_Rounded_MT_Bold.ttf  # Fuente del experimento
└── docs/
    └── codebook_faces.csv  # Códigos de expresiones faciales
```

## Uso

### Ejecutar el Experimento

1. Abra PowerShell en la carpeta del proyecto
2. Ejecute:

```bash
python "home version.py"
```

3. Ingrese el ID del participante en el formato especificado
4. Presione ENTER para iniciar

### Formato del ID de Participante

El ID debe seguir el formato: `ID_CONDICIÓN_MANO_ORDEN`

**Ejemplo:** `4321_E_R_12`

Donde:
- **ID:** Identificador único del participante (ej: 4321)
- **CONDICIÓN:** `C` (Control) o `E` (Experimental)
- **MANO:** `L` (Left/Izquierda) o `R` (Right/Derecha) - mano inicial para responder
- **ORDEN:** Dos dígitos del 1 al 6 que indican el orden de respuestas para cada bloque

### Órdenes de Respuesta Disponibles

1. Neutral - Happy - Sad
2. Happy - Sad - Neutral
3. Sad - Neutral - Happy
4. Neutral - Sad - Happy
5. Happy - Neutral - Sad
6. Sad - Happy - Neutral

## Estructura del Experimento

### 1. Bloque de Práctica 1
- 9 imágenes de prueba
- Mano inicial de respuesta
- Orden de respuestas aleatorio (no usado en bloques experimentales)

### 2. Bloque de Práctica 2
- 9 imágenes de prueba
- Mano contraria
- Orden de respuestas aleatorio diferente

### 3. Bloque Experimental 1
- 60 imágenes (20 por categoría)
- Mano inicial de respuesta
- Orden de respuestas según primer dígito del ID

### 4. Descanso
- El participante puede tomar un descanso
- Cambio de mano de respuesta

### 5. Bloque Experimental 2
- 60 imágenes (20 por categoría)
- Mano contraria
- Orden de respuestas según segundo dígito del ID

## Secuencia de Presentación

Para cada estímulo:
1. **Pantalla en blanco** (500 ms)
2. **Cruz de fijación** (+) (1000 ms)
3. **Imagen facial** en escala de grises (200 ms)
4. **Pantalla de respuesta** con opciones (hasta que el participante responda)
5. **Intervalo inter-estímulo** (1000-1200 ms, aleatorio)

## Teclas de Respuesta

- **C:** Primera opción de respuesta
- **B:** Segunda opción de respuesta
- **M:** Tercera opción de respuesta
- **Espacio:** Continuar entre pantallas
- **ESC:** Salir del experimento (solo en modo debug)

## Archivos de Salida

Los datos se guardan en la carpeta `data/` con el formato:

`YYYY-MM-DD_HH-MM-SS_ID_CONDICIÓN_MANO_ORDEN.csv`

### Columnas del CSV

| Columna | Descripción |
|---------|-------------|
| Sujeto | ID del participante |
| IdImagen | Nombre del archivo de imagen |
| Bloque | Número de bloque (0=práctica, 1=primero, 2=segundo) |
| TReaccion | Tiempo de reacción en milisegundos |
| TipoImagen | Categoría real de la imagen (Happy/Neutral/Sad) |
| OrdenRespuestas | Orden de las opciones presentadas (ej: Neutral-Happy-Sad) |
| Respuesta | Respuesta seleccionada por el participante |
| Acierto | 1=correcta, 0=incorrecta, vacío=práctica |

## Modo Debug

Para activar el modo de depuración, edite el archivo [`home version.py`](home version.py) y cambie:

```python
debug_mode = False
```

a:

```python
debug_mode = True
```

En modo debug:
- Se pueden usar teclas adicionales (ESC para salir, P para saltar)
- Se muestran mensajes de diagnóstico en consola
- Los bloques de práctica guardan datos

## Configuración Adicional

### Puerto Serial (EEG/Triggers)

Si utiliza equipos de EEG, configure el puerto serial en la función [`init_com`](home version.py):

```python
def init_com(address="COM3"):  # Cambie COM3 al puerto correcto
```

### Pantalla Completa

Para desactivar la pantalla completa, edite:

```python
FullScreenShow = True  # Cambie a False
```

## Códigos de Trigger (EEG)

- **254:** Inicio del experimento
- **255:** Fin del experimento
- **244:** Cruz de fijación
- **1-240:** ID de imágenes
- **241-243:** ID de bloques

## Solución de Problemas

### Error: "No se puede abrir el puerto serial"
El puerto serial no está disponible. Si no usa EEG, ignore este mensaje.

### Error: "Error al cargar imagen"
Verifique que la carpeta `media/images/` contenga las subcarpetas Happy, Neutral y Sad con imágenes.

### La fuente no se carga correctamente
Asegúrese de que el archivo `Arial_Rounded_MT_Bold.ttf` esté en la carpeta `media/`.

### El experimento no inicia en pantalla completa
Verifique la configuración de `FullScreenShow` en el código.

## Referencias

- **Codebook:** Ver [docs/codebook_faces.csv](docs/codebook_faces.csv) para códigos de expresiones faciales
- **Tutorial detallado:** Ver [README.txt](README.txt)

## Autor y Contacto

Para soporte técnico o preguntas sobre el experimento, contacte al encargado del laboratorio.

## Licencia

Este software es para uso académico y de investigación.
```