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
#                           DESCRIPCIÓN
# ---------------------------------------------------------------------------
# Gramática Libre de Contexto (GLC) que modela una "herramienta de dibujo"
# sobre el alfabeto del genoma  Σ = { a, c, g, t }. Cada terminal es una orden
# de una tortuga gráfica (estilo Logo / L-System):
#
#     a -> avanzar 1 unidad TRAZANDO (dibuja la línea)
#     c -> girar 90° a la derecha   (clockwise)
#     g -> girar 90° a la izquierda (giro antihorario)
#     t -> avanzar 1 unidad SIN trazar (trasladar, lápiz levantado)
#
# El programa hace dos cosas por cada figura:
#   1) Realiza la DERIVACIÓN por la izquierda desde el símbolo inicial S,
#      mostrando paso a paso cada forma sentencial (tarea 2.2.1: 5 ejemplos).
#   2) INTERPRETA la cadena terminal resultante como órdenes de la tortuga y
#      la dibuja de dos formas: en una cuadrícula ASCII (consola) y en una
#      ventana gráfica real con el módulo turtle, que se abre automáticamente.
#
# Para omitir la ventana gráfica (entorno sin pantalla):
#      python glc_genoma.py --no-turtle
# ---------------------------------------------------------------------------

import sys

# En Windows aseguramos salida UTF-8 para los símbolos Σ, °, etc.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ===========================================================================
#           1) GRAMÁTICA LIBRE DE CONTEXTO  G = (N, Σ, P, S)
# ===========================================================================
#   N (no terminales) : símbolos en MAYÚSCULA  -> S, CUADRADO, L, M, P...
#   Σ (terminales)    : { a, c, g, t }
#   S (símbolo inicial): 'S'
#   P (producciones)  : el diccionario GRAMATICA de abajo
#
# Notación BNF equivalente:
#   <S>          ::= <CUADRADO> | <RECTANGULO> | <ELE> | <ESCALERA> | <DOSCUADROS>
#   <CUADRADO>   ::= <L> c <L> c <L> c <L>
#   <RECTANGULO> ::= <L> c <M> c <L> c <M>
#   <ELE>        ::= c <M> g <L>        (baja el lado vertical y luego la base)
#   <ESCALERA>   ::= <P> <ESCALERA> | <P>
#   <DOSCUADROS> ::= <CUADRADO> t t t <CUADRADO>   (dos figuras separadas por un salto)
#   <L>          ::= a | a <L>          (lado de longitud >= 1)
#   <M>          ::= a | a <M>          (lado de longitud >= 1)
#   <P>          ::= a c a g            (un peldaño de escalera)

GRAMATICA = {
    "S":          [["CUADRADO"], ["RECTANGULO"], ["ELE"], ["ESCALERA"], ["DOSCUADROS"]],
    "CUADRADO":   [["L", "c", "L", "c", "L", "c", "L"]],
    "RECTANGULO": [["L", "c", "M", "c", "L", "c", "M"]],
    "ELE":        [["c", "M", "g", "L"]],
    "ESCALERA":   [["P", "ESCALERA"], ["P"]],
    "DOSCUADROS": [["CUADRADO", "t", "t", "t", "CUADRADO"]],
    "L":          [["a"], ["a", "L"]],
    "M":          [["a"], ["a", "M"]],
    "P":          [["a", "c", "a", "g"]],
}


def es_no_terminal(sym):
    return sym in GRAMATICA


# ===========================================================================
#           2) MOTOR DE DERIVACIÓN POR LA IZQUIERDA
# ===========================================================================
# Recibe una "receta": lista ordenada de pasos (no_terminal, lado_derecho).
# En cada paso reemplaza el no terminal MÁS A LA IZQUIERDA, validando que la
# producción exista realmente en la gramática (rigor formal).

def derivar(receta):
    forma = ["S"]
    historia = [formatear(forma)]

    for nt, rhs in receta:
        i = next((k for k, s in enumerate(forma) if es_no_terminal(s)), -1)
        if i == -1:
            raise ValueError("No quedan no terminales por derivar.")
        if forma[i] != nt:
            raise ValueError(f"Se esperaba derivar <{nt}> pero el más a la izquierda es <{forma[i]}>.")

        if not any(p == rhs for p in GRAMATICA[nt]):
            raise ValueError(f"La producción <{nt}> ::= {' '.join(rhs)} no pertenece a la gramática.")

        forma = forma[:i] + rhs + forma[i + 1:]
        historia.append(formatear(forma))

    cadena = "".join(forma)
    return cadena, historia


def formatear(forma):
    """Muestra una forma sentencial: no terminales entre <> y terminales tal cual."""
    return " ".join(f"<{s}>" if es_no_terminal(s) else s for s in forma)


# --- Generadores de recetas ---
def expandir_lado(nt, n):
    """Expande un lado <X> de longitud n: <X> ::= a <X> ... | a"""
    pasos = [(nt, ["a", nt]) for _ in range(n - 1)]
    pasos.append((nt, ["a"]))
    return pasos


def receta_cuadrado(lado):
    return (
        [("S", ["CUADRADO"]), ("CUADRADO", ["L", "c", "L", "c", "L", "c", "L"])]
        + expandir_lado("L", lado) + expandir_lado("L", lado)
        + expandir_lado("L", lado) + expandir_lado("L", lado)
    )


def receta_rectangulo(largo, ancho):
    return (
        [("S", ["RECTANGULO"]), ("RECTANGULO", ["L", "c", "M", "c", "L", "c", "M"])]
        + expandir_lado("L", largo) + expandir_lado("M", ancho)
        + expandir_lado("L", largo) + expandir_lado("M", ancho)
    )


def receta_ele(largo, ancho):
    # ELE ::= c <M> g <L>  -> primero baja el lado vertical (<M>) y luego la base (<L>)
    return (
        [("S", ["ELE"]), ("ELE", ["c", "M", "g", "L"])]
        + expandir_lado("M", ancho) + expandir_lado("L", largo)
    )


def receta_escalera(peldanos):
    pasos = [("S", ["ESCALERA"])]
    for i in range(peldanos):
        pasos.append(("ESCALERA", ["P", "ESCALERA"] if i < peldanos - 1 else ["P"]))
        pasos.append(("P", ["a", "c", "a", "g"]))
    return pasos


def receta_dos_cuadrados(lado):
    """Dibuja dos cuadrados separados por un salto (usa el terminal 't' de lápiz levantado)."""
    pasos = [("S", ["DOSCUADROS"]),
             ("DOSCUADROS", ["CUADRADO", "t", "t", "t", "CUADRADO"])]
    for _ in range(2):  # cada uno de los dos cuadrados
        pasos.append(("CUADRADO", ["L", "c", "L", "c", "L", "c", "L"]))
        for _ in range(4):  # los cuatro lados del cuadrado
            pasos += expandir_lado("L", lado)
    return pasos


# ===========================================================================
#               3) INTÉRPRETE DE LA TORTUGA GRÁFICA
# ===========================================================================
# Recorre la cadena terminal y calcula los puntos trazados. Como todos los
# giros son de 90° y los avances de 1 unidad, el trazo siempre es ortogonal.

def dibujar(cadena):
    x, y = 0, 0       # posición
    dx, dy = 1, 0     # dirección inicial: hacia el Este
    puntos = {"0,0"}

    for ch in cadena:
        if ch == "a":                 # avanzar trazando
            x += dx
            y += dy
            puntos.add(f"{x},{y}")
        elif ch == "t":               # avanzar sin trazar
            x += dx
            y += dy
        elif ch == "c":               # girar 90° derecha:  (dx,dy)->(dy,-dx)
            dx, dy = dy, -dx
        elif ch == "g":               # girar 90° izquierda: (dx,dy)->(-dy,dx)
            dx, dy = -dy, dx
    return puntos


def render(puntos):
    """Convierte el conjunto de puntos en una cuadrícula ASCII."""
    coords = [tuple(map(int, s.split(","))) for s in puntos]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    salida = ""
    for y in range(max_y, min_y - 1, -1):
        fila = "   "
        for x in range(min_x, max_x + 1):
            fila += "##" if f"{x},{y}" in puntos else "  "
        salida += fila + "\n"
    return salida


# ===========================================================================
#           4) DIBUJO VIRTUAL CON TURTLE (ventana gráfica opcional)
# ===========================================================================
# Misma semántica que el intérprete ASCII, pero trazada por la tortuga real de
# Python. Cada figura se dibuja en su propia zona de la ventana con un color y
# su etiqueta. La ventana se abre automáticamente al ejecutar el programa.
def _trazar_turtle(t, cadena, unidad):
    for ch in cadena:
        if ch == "a":            # avanzar trazando
            t.pendown()
            t.forward(unidad)
        elif ch == "t":          # avanzar sin trazar (lápiz levantado)
            t.penup()
            t.forward(unidad)
            t.pendown()
        elif ch == "c":          # girar 90° a la derecha
            t.right(90)
        elif ch == "g":          # girar 90° a la izquierda
            t.left(90)


COLORES_TURTLE = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"]
# Punto donde inicia el trazo de cada figura (coords de ventana, mirando al Este).
# Las posiciones se separan lo suficiente para que las 5 figuras no se solapen;
# la figura e) es alta (dos cuadrados con salto), por eso va en la fila inferior
# centrada, junto a la escalera.
ORIGENES_TURTLE = [(-360, 200), (-160, 200), (120, 200), (-360, -40), (-120, -110)]


def _tope_figura(cadena, ox, oy, unidad):
    """Devuelve la coordenada Y más alta que alcanza el trazo (para situar la etiqueta encima)."""
    x, y, dx, dy = ox, oy, 1, 0
    tope = oy
    for ch in cadena:
        if ch in ("a", "t"):
            x += dx * unidad
            y += dy * unidad
            if ch == "a":
                tope = max(tope, y)
        elif ch == "c":
            dx, dy = dy, -dx
        elif ch == "g":
            dx, dy = -dy, dx
    return tope


def dibujar_turtle(figuras, unidad=30):
    import turtle  # import diferido: solo se necesita en el modo gráfico

    pantalla = turtle.Screen()
    pantalla.setup(width=900, height=650)
    pantalla.title("Atomic Code - GLC de dibujo sobre el genoma  (a, c, g, t)")
    pantalla.bgcolor("white")

    t = turtle.Turtle()
    t.speed(0)
    t.pensize(3)

    for (nombre, receta), origen, color in zip(figuras, ORIGENES_TURTLE, COLORES_TURTLE):
        cadena, _ = derivar(receta)
        ox, oy = origen

        # etiqueta de la figura, situada encima del punto más alto del trazo
        t.penup()
        t.goto(ox, _tope_figura(cadena, ox, oy, unidad) + 12)
        t.color("black")
        t.write(nombre, font=("Arial", 10, "bold"))

        # posicionar e iniciar el trazo
        t.goto(ox, oy)
        t.setheading(0)          # 0 grados = Este, igual que el intérprete ASCII
        t.color(color)
        t.pendown()
        _trazar_turtle(t, cadena, unidad)

    t.hideturtle()
    pantalla.exitonclick()       # la ventana se cierra al hacer clic


# ===========================================================================
#           5) DEFINICIÓN DE LOS 5 EJEMPLOS Y EJECUCIÓN
# ===========================================================================
FIGURAS = [
    ("a) CUADRADO (lado 3)",      receta_cuadrado(3)),
    ("b) RECTÁNGULO (5 x 3)",     receta_rectangulo(5, 3)),
    ("c) FIGURA EN L (4 y 3)",    receta_ele(4, 3)),
    ("d) ESCALERA (3 peldaños)",  receta_escalera(3)),
    ("e) DOS CUADRADOS (con salto, usa 't')", receta_dos_cuadrados(2)),
]


def ejecutar():
    print("===========================================================")
    print("     GLC para dibujo sobre el genoma  Σ = { a, c, g, t }")
    print("                  Equipo: Atomic Code")
    print("===========================================================")
    print("\nSemántica de la tortuga:")
    print("   a = avanzar trazando     c = girar 90° derecha")
    print("   g = girar 90° izquierda  t = avanzar sin trazar\n")

    for nombre, receta in FIGURAS:
        cadena, historia = derivar(receta)

        print("===========================================================")
        print(" " + nombre)
        print("===========================================================")
        print("\n  Derivación por la izquierda:")
        for idx, forma in enumerate(historia):
            flecha = "  S        " if idx == 0 else "   =>      "
            print(f"{flecha} {forma}")
        print(f"\n  Cadena generada (w): {cadena}")
        print(f"  Longitud: {len(cadena)} símbolos del alfabeto Σ\n")
        print("  Dibujo resultante:")
        print(render(dibujar(cadena)))

if __name__ == "__main__":
    ejecutar()

    # Al ejecutar se abre además la ventana gráfica (turtle) con las figuras.
    # Para omitirla (por ejemplo en un entorno sin pantalla) usa: --no-turtle
    if "--no-turtle" not in sys.argv:
        print("===========================================================")
        print(" Abriendo la ventana gráfica (turtle)...")
        print(" Haz clic en la ventana para cerrarla.")
        print("===========================================================")
        try:
            dibujar_turtle(FIGURAS)
        except Exception as error:
            print(f"\n[Aviso] No se pudo abrir la ventana gráfica (turtle): {error}")
            print("Las figuras quedan disponibles arriba en modo ASCII.")
