# Tema 3 - Lenguajes y Gramáticas Formales

### Equipo: **Atomic Code**
> _Segmentando el código, construyendo la lógica_

**Asignatura:** Lenguaje y Compiladores - 2026-I - Sección 01

**Universidad Nacional Experimental de Guayana (UNEG)**

---

## Integrantes

| Integrante | Cédula de Identidad |
|------------|---------------------|
| Victor Vargas | 30.697.219 |
| Keibel Guilarte | 28.726.605 |
| Oriana Márquez | 31.354.299 |
| Jeanny Monagas | 30.857.471 |

---

## Resumen del tema

El **Tema 3** aborda los fundamentos teóricos del procesamiento de lenguajes, es
decir, las herramientas formales que permiten **generar** y **reconocer** un
lenguaje *L*. Es la base sobre la que se construyen los analizadores léxicos y
sintácticos de cualquier compilador o intérprete. Los conceptos centrales son:

- **Alfabetos y palabras:** un alfabeto (Σ) es un conjunto finito de símbolos y
  una palabra es una secuencia finita de esos símbolos.
- **Lenguajes formales:** un conjunto (matemático) de cadenas válidas sobre Σ.
- **Gramáticas formales:** un conjunto finito de reglas de producción que generan
  todas las cadenas válidas de un lenguaje y permiten validar si una cadena
  pertenece a él.
- **Jerarquía de Chomsky:** clasificación de las gramáticas en cuatro tipos
  (Tipo 0 a Tipo 3) según el poder expresivo de sus reglas y la capacidad
  computacional necesaria para procesarlas.
- **Expresiones regulares y autómatas finitos:** la materialización práctica de
  la teoría; son la piedra angular del análisis léxico (reconocimiento de
  patrones con memoria limitada).

Este repositorio contiene los **dos casos prácticos con código funcional**
exigidos por la guía: un reconocedor de ajedrez (PGN) basado en un autómata
finito, y una gramática libre de contexto de dibujo sobre el alfabeto del genoma.

---

## Estructura del repositorio

```
Tema 3 - Lenguajes y compiladores - Atomic Code/
├── README.md
├── Pgn-ajedrez - Atomic Code/
│   └── afd_pgn.py        # Caso Ajedrez: AFD + Regex que reconoce jugadas PGN
└── Genoma - Atomic Code/
    └── glc_genoma.py     # Caso Genoma: GLC de dibujo sobre Σ = {a, c, g, t}
```

### `Pgn-ajedrez - Atomic Code/` - De la expresión al autómata (Caso Ajedrez)
Reconoce un subconjunto del lenguaje **PGN** (Portable Game Notation). Implementa
un **Autómata Finito Determinístico (AFD)** mediante una tabla de transiciones
explícita y la **Expresión Regular equivalente**. Por cada jugada muestra la
traza de estados del AFD y verifica que su veredicto coincide con el de la Regex.
Reconoce: jugadas de pieza (`Nf3`, `Bxe5`), de peón (`e4`, `exd5`), enroques
(`O-O`, `O-O-O`) y sufijos de jaque/mate (`Nf3+`, `Qh5#`).

### `Genoma - Atomic Code/` - Derivación y modelado (Caso Genoma)
Una **Gramática Libre de Contexto (GLC)** que modela una herramienta de dibujo
sobre el alfabeto del genoma **Σ = {a, c, g, t}**, donde cada terminal es una
orden de una tortuga gráfica (`a` avanzar, `c` y `g` girar, `t` trasladar). El
programa realiza la **derivación por la izquierda** paso a paso de 5 figuras
(cuadrado, rectángulo, L, escalera y dos cuadrados con salto) y luego **dibuja**
cada cadena resultante de dos formas: en una cuadrícula ASCII (consola) y en una
ventana gráfica real con `turtle`, que se abre automáticamente al ejecutar.

---

## Requisitos

- **Python** versión 3.7 o superior. (No requiere dependencias externas.)
  - Verifica tu instalación con: `python --version`
  - Si no lo tienes, descárgalo desde <https://www.python.org>.

## Instalación y ejecución

1. Clona o descarga este repositorio y entra en la carpeta del proyecto:

   ```bash
   cd "Tema 3 - Lenguajes y compiladores - Atomic Code"
   ```

2. Ejecuta cada caso práctico invocando Python sobre cada archivo:

   ```bash
   python "Pgn-ajedrez - Atomic Code/afd_pgn.py"    # Reconocedor de jugadas PGN (Ajedrez)
   python "Genoma - Atomic Code/glc_genoma.py"      # GLC de dibujo sobre el genoma
   ```

   > En algunos sistemas el comando es `python3` en lugar de `python`.

   El programa del genoma muestra la derivación y el dibujo ASCII en la consola
   y, además, **abre automáticamente una ventana gráfica** (`turtle`) con las 5
   figuras a color; la ventana se cierra al hacer clic. Esto requiere `tkinter`
   (incluido por defecto en la mayoría de instalaciones de Python). Para omitir
   la ventana gráfica (por ejemplo en un entorno sin pantalla):

   ```bash
   python "Genoma - Atomic Code/glc_genoma.py" --no-turtle
   ```

No hay que instalar paquetes: ambos programas usan únicamente la biblioteca
estándar de Python (`re` y `sys`).

---

_Atomic Code - Segmentando el código, construyendo la lógica._
