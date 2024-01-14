import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt


def validar_entrada_numero(entrada, minimo, maximo):
    """
    Valida si la entrada es un número dentro de un rango específico.
    """
    try:
        valor = float(entrada)
        if minimo <= valor <= maximo:
            return valor
        else:
            raise ValueError
    except ValueError:
        return None

def generar_poblacion_inicial(tamano_poblacion, longitud_individuo):
    """
    Genera la población inicial de individuos representados como cadenas de bits.
    """
    return [''.join(random.choice('01') for _ in range(longitud_individuo)) for _ in range(tamano_poblacion)]

def formar_parejas(poblacion):
    """
    Forma parejas de individuos de la población para la cruza.
    Cada individuo se cruzará con todos los demás.
    """
    parejas = []
    for i in range(len(poblacion)):
        for j in range(i + 1, len(poblacion)):
            parejas.append((poblacion[i], poblacion[j]))
    return parejas

def cruza(individuo1, individuo2, punto_cruza):
    """
    Cruza dos individuos en un punto fijo para crear dos descendientes.
    """
    descendiente1 = individuo1[:punto_cruza] + individuo2[punto_cruza:]
    descendiente2 = individuo2[:punto_cruza] + individuo1[punto_cruza:]
    return descendiente1, descendiente2

def aplicar_cruza(parejas, punto_cruza):
    """
    Aplica la cruza a todas las parejas formadas.
    """
    descendientes = []
    for ind1, ind2 in parejas:
        descendiente1, descendiente2 = cruza(ind1, ind2, punto_cruza)
        descendientes.append(descendiente1)
        descendientes.append(descendiente2)
    return descendientes

def mutar(individuo, probabilidad_mutacion):
    """
    Aplica mutación a un individuo. Cada gen puede sufrir una negación del bit con una cierta probabilidad.
    """
    individuo_mutado = ''
    for gen in individuo:
        if random.random() < probabilidad_mutacion:
            individuo_mutado += '0' if gen == '1' else '1'
        else:
            individuo_mutado += gen
    return individuo_mutado

def aplicar_mutacion(poblacion, probabilidad_mutacion):
    """
    Aplica la mutación a cada individuo en la población.
    """
    return [mutar(individuo, probabilidad_mutacion) for individuo in poblacion]

def evaluar_fitness(individuo):
    """
    Evalúa la aptitud (fitness) de un individuo. 
    Esta es una función genérica y debe ser adaptada al problema específico.
    """
    return sum(int(gen) for gen in individuo)

def aplicar_poda(poblacion, tamano_deseado):
    """
    Aplica la poda a la población, reduciendo su tamaño y manteniendo al mejor individuo.
    """
    poblacion_ordenada = sorted(poblacion, key=evaluar_fitness, reverse=True)
    mejor_individuo = poblacion_ordenada[0]
    poblacion_reducida = random.sample(poblacion_ordenada[1:], tamano_deseado - 1)
    poblacion_reducida.append(mejor_individuo)
    return poblacion_reducida


def iniciar_algoritmo():
    tam_poblacion = validar_entrada_numero(tamanio_poblacion.get(), 1, 1000)
    prob_mut = validar_entrada_numero(prob_mutacion.get(), 0, 1)
    num_gen = validar_entrada_numero(num_generaciones.get(), 1, 1000)
    longitud_individuo = validar_entrada_numero(longitud_individuos.get(), 1, 100)

    if not all([tam_poblacion, prob_mut, num_gen, longitud_individuo]):
        print("Por favor, ingresa valores válidos para todos los parámetros.")
        return

    num_gen = int(num_gen)
    
    poblacion = generar_poblacion_inicial(int(tam_poblacion), int(longitud_individuo))


    # Listas para almacenar estadísticas de cada generación
    fitness_medio_por_generacion = []
    mejor_fitness_por_generacion = []

    for generacion in range(num_gen):
        parejas = formar_parejas(poblacion)
        descendientes = aplicar_cruza(parejas, punto_cruza=3)  # Punto de cruza fijo
        poblacion = aplicar_mutacion(descendientes, prob_mut)
        poblacion = aplicar_poda(poblacion, int(tam_poblacion))

        # Calcular el fitness de cada individuo en la población
        fitness_de_la_poblacion = [evaluar_fitness(individuo) for individuo in poblacion]
        fitness_medio = sum(fitness_de_la_poblacion) / len(fitness_de_la_poblacion)
        mejor_fitness = max(fitness_de_la_poblacion)
        fitness_medio_por_generacion.append(fitness_medio)
        mejor_fitness_por_generacion.append(mejor_fitness)

    # Mostrar las gráficas al finalizar todas las generaciones
    plt.figure(figsize=(10, 5))

    # Gráfico de la evolución del fitness medio y mejor fitness
    plt.subplot(1, 2, 1)
    plt.plot(fitness_medio_por_generacion, label='Fitness Medio')
    plt.plot(mejor_fitness_por_generacion, label='Mejor Fitness')
    plt.title('Evolución del Fitness')
    plt.xlabel('Generación')
    plt.ylabel('Fitness')
    plt.legend()

    # Gráfico de los individuos en la última generación
    plt.subplot(1, 2, 2)
    plt.hist(fitness_de_la_poblacion, bins=20)
    plt.title('Distribución del Fitness en la Última Generación')
    plt.xlabel('Fitness')
    plt.ylabel('Cantidad de Individuos')

    plt.tight_layout()
    plt.show()


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Algoritmo Genético")

# Marco para parámetros de entrada
frame_entradas = ttk.Frame(ventana)
frame_entradas.grid(column=0, row=0, sticky='ew')

ttk.Label(frame_entradas, text="Tamaño de la Población:").grid(column=0, row=0)
tamanio_poblacion = ttk.Entry(frame_entradas)
tamanio_poblacion.grid(column=1, row=0)

ttk.Label(frame_entradas, text="Probabilidad de Mutación:").grid(column=0, row=1)
prob_mutacion = ttk.Entry(frame_entradas)
prob_mutacion.grid(column=1, row=1)

ttk.Label(frame_entradas, text="Número de Generaciones:").grid(column=0, row=2)
num_generaciones = ttk.Entry(frame_entradas)
num_generaciones.grid(column=1, row=2)

ttk.Label(frame_entradas, text="Longitud de los Individuos:").grid(column=0, row=3)
longitud_individuos = ttk.Entry(frame_entradas)
longitud_individuos.grid(column=1, row=3)

# Botón para iniciar el algoritmo
ttk.Button(ventana, text="Iniciar Algoritmo", command=iniciar_algoritmo).grid(column=0, row=1, columnspan=2)

# Espacio reservado para futuras visualizaciones de resultados (estadísticas, gráficas, etc.)

ventana.mainloop()