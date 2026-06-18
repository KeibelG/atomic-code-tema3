# Lenguaje:   Python 3
# Asignatura: Lenguajes y compiladores
# Equipo:     Atomic Code
#             Segmentando el código, construyendo la lógica
#
# Integrantes:
#   - Victor Vargas    C.I: 30.697.219
#   - Keibel Guilarte  C.I: 28.726.605
#   - Oriana Márquez   C.I: 31.354.299
#   - Jeanny Monagas   C.I: 30.857.471
#
# ---------------------------------------------------------------------------
# DESCRIPCIÓN
# ---------------------------------------------------------------------------
# Reconocedor de un subconjunto del lenguaje PGN (Portable Game Notation) del
# ajedrez. El programa implementa un Autómata Finito Determinístico (AFD)
# "a mano" mediante una tabla de transiciones explícita y, en paralelo, la
# Expresión Regular equivalente. Por cada jugada de prueba ejecuta el AFD
# símbolo a símbolo (mostrando la traza de estados) y verifica que el
# veredicto del AFD coincida con el de la Regex, demostrando su equivalencia.
#
# Subconjunto del PGN reconocido (movimientos básicos):
#   - Jugada de pieza:   [pieza][captura?][columna][fila]   ej.  Nf3  Bxe5  Qd1
#   - Jugada de peón:    [columna][fila]                     ej.  e4   d5
#   - Captura de peón:   [columna]x[columna][fila]           ej.  exd5
#   - Enroque corto:     O-O
#   - Enroque largo:     O-O-O
#   - Sufijo opcional:   + (jaque)   # (jaque mate)          ej.  Qh5#  Nf3+
#
# Además, al ejecutar se abre una ventana gráfica con el diagrama de estados
# del autómata (para omitirla:  python afd_pgn.py --no-turtle).
# ---------------------------------------------------------------------------

import re
import sys

# En Windows aseguramos salida UTF-8 para los símbolos δ, °, etc.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ===========================================================================
# 1) ALFABETO (Σ) Y CLASIFICACIÓN DE SÍMBOLOS
# ===========================================================================
# El alfabeto se agrupa en clases para que la tabla de transiciones sea legible:
#   PIEZA = { K, Q, R, B, N }   (Rey, Dama, Torre, Alfil, Caballo)
#   FILE  = { a, b, c, d, e, f, g, h }   (columnas del tablero)
#   RANK  = { 1, 2, 3, 4, 5, 6, 7, 8 }   (filas del tablero)
#   y los símbolos literales: x  O  -  +  #
PIEZAS = "KQRBN"
COLUMNAS = "abcdefgh"
FILAS = "12345678"


def clase(ch):
    """Devuelve la clase del símbolo de entrada (o el propio carácter si es literal)."""
    if ch in PIEZAS:
        return "PIEZA"
    if ch in COLUMNAS:
        return "FILE"
    if ch in FILAS:
        return "RANK"
    return ch  # x, O, -, +, #  (símbolos literales)


# ===========================================================================
# 2) DEFINICIÓN FORMAL DEL AFD  M = (Q, Σ, δ, q0, F)
# ===========================================================================
# Q  : conjunto de estados (las claves de TRANSICIONES + estados de aceptación)
# q0 : estado inicial = 'q0'
# F  : conjunto de estados de aceptación = ACEPTACION
# δ  : función de transición = TRANSICIONES[estado][clase] -> estado
ESTADO_INICIAL = "q0"
ACEPTACION = {"qF", "q8", "q10", "qChk"}

TRANSICIONES = {
    # --- inicio: decide qué tipo de jugada se está leyendo ---
    "q0": {"PIEZA": "q1", "FILE": "q3", "O": "q6"},

    # --- rama de jugada de PIEZA:  [pieza] [x?] [columna] [fila] ---
    "q1": {"x": "q2", "FILE": "q5"},   # leída la pieza; puede venir captura o columna
    "q2": {"FILE": "q5"},              # leída la 'x'; falta columna
    "q5": {"RANK": "qF"},              # leída la columna; falta la fila -> aceptación

    # --- rama de jugada de PEÓN:  [columna] [fila]  |  [columna] x [columna] [fila] ---
    "q3": {"RANK": "qF", "x": "q4"},   # leída columna inicial; fila (e4) o captura (exd5)
    "q4": {"FILE": "q5"},              # captura de peón: leída la 'x', falta columna destino

    # --- rama de ENROQUE:  O-O  |  O-O-O ---
    "q6": {"-": "q7"},
    "q7": {"O": "q8"},                 # O-O  -> aceptación
    "q8": {"-": "q9", "+": "qChk", "#": "qChk"},
    "q9": {"O": "q10"},                # O-O-O -> aceptación
    "q10": {"+": "qChk", "#": "qChk"},

    # --- sufijo de jaque / jaque mate desde una jugada ya válida ---
    "qF": {"+": "qChk", "#": "qChk"},  # jugada normal aceptada
    "qChk": {},                        # ya se leyó + o # : no admite más símbolos
}


# ===========================================================================
# 3) MOTOR DEL AFD: ejecuta la cadena símbolo a símbolo y registra la traza
# ===========================================================================
def reconocer(cadena):
    estado = ESTADO_INICIAL
    traza = []

    for ch in cadena:
        simbolo = clase(ch)
        destino = TRANSICIONES.get(estado, {}).get(simbolo)
        traza.append({"desde": estado, "lee": ch, "clase": simbolo, "hacia": destino or "(rechazo)"})

        if destino is None:
            return {
                "aceptada": False,
                "traza": traza,
                "estado_final": estado,
                "motivo": f"No hay transición δ({estado}, '{ch}')",
            }
        estado = destino

    aceptada = estado in ACEPTACION
    return {
        "aceptada": aceptada,
        "traza": traza,
        "estado_final": estado,
        "motivo": "Estado final de aceptación" if aceptada
                  else f"'{estado}' no es estado de aceptación (cadena incompleta)",
    }


# ===========================================================================
# 4) EXPRESIÓN REGULAR EQUIVALENTE (tarea 2.4.3)
# ===========================================================================
# Misma definición del subconjunto, expresada como Regex:
#   pieza:    [KQRBN]x?[a-h][1-8]
#   peón:     [a-h]( [1-8] | x[a-h][1-8] )
#   enroque:  O-O(-O)?
#   sufijo:   [+#]?
REGEX_PGN = re.compile(r"^([KQRBN]x?[a-h][1-8]|[a-h](?:[1-8]|x[a-h][1-8])|O-O(?:-O)?)[+#]?$")


# ===========================================================================
# 5) CASOS DE PRUEBA Y EJECUCIÓN
# ===========================================================================
VALIDAS = ["e4", "d5", "Nf3", "Bb5", "Qxd8", "exd5", "Rxe1", "O-O", "O-O-O", "Nf3+", "Qh5#"]
INVALIDAS = ["e9", "Z3", "e", "O-O-O-O", "4e", "xe4", "e44", "Nf", "Pxe4"]


def imprimir_traza(traza):
    for p in traza:
        print(f"     δ({p['desde']:<4}, '{p['lee']}'  [{p['clase']}]) -> {p['hacia']}")


def probar(jugada):
    r = reconocer(jugada)
    por_regex = bool(REGEX_PGN.match(jugada))
    coinciden = "OK" if r["aceptada"] == por_regex else "¡DISCREPANCIA!"
    veredicto = "ACEPTADA" if r["aceptada"] else "RECHAZADA"

    print(f'\n  "{jugada}"  ->  {veredicto}   (Regex: {"acepta" if por_regex else "rechaza"}) [{coinciden}]')
    print(f"     {r['motivo']}")
    imprimir_traza(r["traza"])


# ===========================================================================
# 6) DIAGRAMA VISUAL DEL AFD (ventana gráfica con turtle)
# ===========================================================================
# Dibuja el autómata como un grafo: cada estado es un círculo (doble círculo si
# es de aceptación) y cada transición es una flecha etiquetada con su símbolo.
# Las posiciones se eligieron para que ninguna flecha atraviese un estado.
# El estado inicial es q0; los de aceptación son qF, q8, q10 y qChk.
_POS_ESTADOS = {
    "q0": (-520, 0),
    "q1": (-330, 250), "q2": (-150, 250),
    "q3": (-330, 0), "q4": (-150, 110), "q5": (20, 110),
    "qF": (190, 0), "qChk": (360, 0),
    "q6": (-330, -200), "q7": (-150, -200), "q8": (20, -200),
    "q9": (180, -200), "q10": (340, -200),
}
# (origen, destino, etiqueta)  -- la etiqueta usa la misma notación que la Regex
_ARISTAS = [
    ("q0", "q1", "[KQRBN]"), ("q0", "q3", "[a-h]"), ("q0", "q6", "O"),
    ("q1", "q2", "x"), ("q1", "q5", "[a-h]"), ("q2", "q5", "[a-h]"),
    ("q3", "q4", "x"), ("q3", "qF", "[1-8]"), ("q4", "q5", "[a-h]"),
    ("q5", "qF", "[1-8]"),
    ("q6", "q7", "-"), ("q7", "q8", "O"), ("q8", "q9", "-"), ("q9", "q10", "O"),
    ("qF", "qChk", "+,#"), ("q8", "qChk", "+,#"), ("q10", "qChk", "+,#"),
]
_RADIO = 34


def _flecha(t, x1, y1, x2, y2, etiqueta):
    import math
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    sx, sy = x1 + ux * _RADIO, y1 + uy * _RADIO   # sale del borde del estado origen
    ex, ey = x2 - ux * _RADIO, y2 - uy * _RADIO   # llega al borde del estado destino

    t.color("#555555")
    t.penup(); t.goto(sx, sy); t.pendown(); t.goto(ex, ey)

    # punta de flecha
    ang = math.atan2(uy, ux)
    for a in (ang + math.radians(152), ang - math.radians(152)):
        t.penup(); t.goto(ex, ey); t.pendown()
        t.goto(ex + 12 * math.cos(a), ey + 12 * math.sin(a))

    # etiqueta en el medio, desplazada perpendicular a la flecha
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    t.penup(); t.goto(mx - uy * 14, my + ux * 14 - 6)
    t.color("#b00000")
    t.write(etiqueta, align="center", font=("Consolas", 10, "bold"))


def _estado(t, x, y, nombre, aceptacion):
    t.color("#1f3b73")
    t.penup(); t.goto(x, y - _RADIO); t.setheading(0); t.pendown()
    t.circle(_RADIO)
    if aceptacion:                       # doble círculo para estados de aceptación
        t.penup(); t.goto(x, y - (_RADIO - 6)); t.pendown()
        t.circle(_RADIO - 6)
    t.penup(); t.goto(x, y - 9)
    t.write(nombre, align="center", font=("Arial", 12, "bold"))


def dibujar_automata():
    import turtle

    aceptacion = {"qF", "q8", "q10", "qChk"}
    pantalla = turtle.Screen()
    pantalla.setup(width=1320, height=780)
    pantalla.title("Atomic Code - AFD del PGN (Ajedrez)")
    pantalla.bgcolor("white")
    pantalla.tracer(0)                   # dibuja todo de una vez (sin animación lenta)

    t = turtle.Turtle()
    t.hideturtle(); t.speed(0); t.pensize(2)

    # 1) flechas (debajo de los estados)
    for origen, destino, etiqueta in _ARISTAS:
        x1, y1 = _POS_ESTADOS[origen]
        x2, y2 = _POS_ESTADOS[destino]
        _flecha(t, x1, y1, x2, y2, etiqueta)

    # 2) flecha de entrada al estado inicial q0
    x0, y0 = _POS_ESTADOS["q0"]
    t.color("#555555")
    t.penup(); t.goto(x0 - 95, y0); t.pendown(); t.goto(x0 - _RADIO, y0)
    t.penup(); t.goto(x0 - _RADIO, y0); t.pendown()
    t.goto(x0 - _RADIO - 11, y0 + 6)
    t.penup(); t.goto(x0 - _RADIO, y0); t.pendown()
    t.goto(x0 - _RADIO - 11, y0 - 6)
    t.penup(); t.goto(x0 - 95, y0 + 12)
    t.color("#1f3b73"); t.write("inicio", align="center", font=("Arial", 10, "italic"))

    # 3) estados (encima de las flechas)
    for nombre, (x, y) in _POS_ESTADOS.items():
        _estado(t, x, y, nombre, nombre in aceptacion)

    # 4) leyenda
    t.color("black")
    t.penup(); t.goto(-560, -320)
    t.write("Inicial: q0    Aceptacion (doble circulo): qF, q8, q10, qChk",
            align="left", font=("Arial", 10, "bold"))
    t.penup(); t.goto(-560, -345)
    t.write("[KQRBN]=pieza   [a-h]=columna   [1-8]=fila   x=captura   O,-=enroque   +,#=jaque/mate",
            align="left", font=("Arial", 9, "normal"))

    pantalla.update()
    pantalla.exitonclick()               # la ventana se cierra al hacer clic


def ejecutar():
    print("===========================================================")
    print(" AFD para el reconocimiento de jugadas PGN (Ajedrez)")
    print(" Equipo: Atomic Code")
    print("===========================================================\n")
    print("Regex equivalente: " + REGEX_PGN.pattern + "\n")

    print("-----------------------------------------------------------")
    print(" Jugadas VÁLIDAS (deben ser aceptadas)")
    print("-----------------------------------------------------------")
    for jugada in VALIDAS:
        probar(jugada)

    print("\n-----------------------------------------------------------")
    print(" Jugadas INVÁLIDAS (deben ser rechazadas)")
    print("-----------------------------------------------------------")
    for jugada in INVALIDAS:
        probar(jugada)


if __name__ == "__main__":
    ejecutar()

    # Al ejecutar se abre además una ventana con el diagrama de estados del AFD.
    # Para omitirla (por ejemplo en un entorno sin pantalla) usa: --no-turtle
    if "--no-turtle" not in sys.argv:
        print("\n===========================================================")
        print(" Abriendo el diagrama del autómata (ventana gráfica)...")
        print(" Haz clic en la ventana para cerrarla.")
        print("===========================================================")
        try:
            dibujar_automata()
        except Exception as error:
            print(f"\n[Aviso] No se pudo abrir la ventana gráfica: {error}")
