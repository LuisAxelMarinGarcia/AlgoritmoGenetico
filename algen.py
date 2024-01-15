import tkinter as tk
import random
import itertools
import math
import matplotlib.pyplot as plt
import sympy as sp


def cruzar_en_punto_fijo(individuo1, individuo2, punto_cruza):
    nuevo_individuo1 = individuo1[:punto_cruza] + individuo2[punto_cruza:]
    nuevo_individuo2 = individuo2[:punto_cruza] + individuo1[punto_cruza:]
    return nuevo_individuo1, nuevo_individuo2

def formar_parejas(poblacion):
    # Estrategia A5: Todos con todos
    parejas = list(itertools.combinations(poblacion, 2))
    return parejas

def mutar_individuo(individuo, prob_mutacion_gen):
    # Mutar cada gen del individuo con la probabilidad dada
    return [mutar_gen(gen, prob_mutacion_gen) for gen in individuo]

def mutar_gen(gen, prob_mutacion_gen):
    # Decidir si el gen muta o no
    if random.random() < prob_mutacion_gen:
        return 1 - gen  # Negación del bit (cambia 0 por 1 o 1 por 0)
    else:
        return gen
    
def binario_a_decimal(binario, intervalo_inferior, intervalo_superior):
    """Convierte una secuencia binaria a un valor decimal dentro de un intervalo dado."""
    decimal = sum(val * (2 ** idx) for idx, val in enumerate(reversed(binario)))
    # Escalar el valor decimal al intervalo especificado
    max_decimal = 2 ** len(binario) - 1
    return intervalo_inferior + (decimal / max_decimal) * (intervalo_superior - intervalo_inferior)

def evaluar_fitness(individuo, intervalo_inferior, intervalo_superior, formula_str):
    x = binario_a_decimal(individuo, intervalo_inferior, intervalo_superior)
    x_simbolico = sp.symbols('x')

    try:
        formula = sp.sympify(formula_str)
        fitness = formula.subs(x_simbolico, x)
        if isinstance(fitness, sp.Number):  # Verificar que el resultado es un número
            return float(fitness)
        else:
            print("El resultado de la fórmula no es un número.")
            return 0  # O manejar de otra forma
    except (sp.SympifyError, TypeError):
        print("Error al analizar la expresión.")
        return 0  # O manejar de otra forma


def podar_poblacion(poblacion_con_fitness, tamano_maximo):
    # Asegurarse de mantener al mejor individuo
    mejor_individuo = max(poblacion_con_fitness, key=lambda item: item[1])
    
    # Eliminar individuos al azar si la población excede el tamaño máximo
    while len(poblacion_con_fitness) > tamano_maximo:
        poblacion_con_fitness.pop(random.randint(0, len(poblacion_con_fitness) - 1))
    
    # Reinsertar el mejor individuo si fue eliminado
    if mejor_individuo not in poblacion_con_fitness:
        poblacion_con_fitness.append(mejor_individuo)

    # Regresar solo los individuos sin el valor de fitness
    return [individuo for individuo, _ in poblacion_con_fitness]


import matplotlib.pyplot as plt

def iniciar_proceso(modo):
    try:
        # Obtener y validar los parámetros de la interfaz
        tamano_poblacion = int(entradas["Ingrese la población inicial"].get())
        num_bits = int(entradas["Ingrese la resolución deseable"].get())
        prob_mutacion_gen = float(entradas["Ingrese la probabilidad de mutación del gen"].get())
        prob_mutacion_individuo = float(entradas["Ingrese la probabilidad de mutación del individuo"].get())
        tamano_maximo = int(entradas["Ingrese la población máxima"].get())
        intervalo_inferior = float(entradas["Intervalo Inferior"].get())
        intervalo_superior = float(entradas["Intervalo Superior"].get())
        num_iteraciones = int(entradas["Ingrese el número de iteraciones"].get())
        prob_cruza = float(entradas["Ingrese la probabilidad de cruza"].get())
        formula_str = entradas["Ingrese la fórmula"].get()  # Obtener la fórmula ingresada por el usuario
    except ValueError:
        print("Por favor, ingresa valores válidos en todos los campos.")
        return

    fitness_medio_por_generacion = []
    mejor_fitness_por_generacion = []
    peor_fitness_por_generacion = []

    # Inicializar la población
    poblacion = [[random.randint(0, 1) for _ in range(num_bits)] for _ in range(tamano_poblacion)]

    for _ in range(num_iteraciones):
        parejas = formar_parejas(poblacion)
        nueva_poblacion = []

        # Cruzamiento
        for ind1, ind2 in parejas:
            if random.random() < prob_cruza:
                punto_cruza = random.randint(1, len(ind1) - 1)
                descendiente1, descendiente2 = cruzar_en_punto_fijo(ind1, ind2, punto_cruza)
                nueva_poblacion.extend([descendiente1, descendiente2])
            else:
                nueva_poblacion.extend([ind1, ind2])

        # Mutación
        nueva_poblacion = [mutar_individuo(ind, prob_mutacion_gen) if random.random() < prob_mutacion_individuo else ind for ind in nueva_poblacion]

        # Evaluación de fitness y poda
        poblacion_con_fitness = [(ind, evaluar_fitness(ind, intervalo_inferior, intervalo_superior, formula_str)) for ind in nueva_poblacion]
        
        # Ajuste para maximizar o minimizar
        invertir_fitness = modo == "minimizar"
        if invertir_fitness:
            poblacion_con_fitness = [(ind, -fitness) for ind, fitness in poblacion_con_fitness]

        poblacion = podar_poblacion(poblacion_con_fitness, tamano_maximo)

        # Calcular estadísticas
        fitness_total = sum(fitness for _, fitness in poblacion_con_fitness)
        mejor_fitness = max(fitness for _, fitness in poblacion_con_fitness)
        peor_fitness = min(fitness for _, fitness in poblacion_con_fitness)
        fitness_medio = fitness_total / len(poblacion_con_fitness)

        # Ajuste en el gráfico para reflejar correctamente la minimización
        if invertir_fitness:
            mejor_fitness = -mejor_fitness
            peor_fitness = -peor_fitness
            fitness_medio = -fitness_medio

        fitness_medio_por_generacion.append(fitness_medio)
        mejor_fitness_por_generacion.append(mejor_fitness)
        peor_fitness_por_generacion.append(peor_fitness)
        



    # Mostrar gráficos
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(fitness_medio_por_generacion, label='Caso Promedio', color='green')
    plt.plot(mejor_fitness_por_generacion, label='Mejor Caso', color='blue')
    plt.plot(peor_fitness_por_generacion, label='Peor Caso', color='orange')
    plt.xlabel('Generación')
    plt.ylabel('Fitness')
    plt.title('Evolución del Fitness')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.hist([fitness for _, fitness in poblacion_con_fitness], bins=10, edgecolor='black')
    plt.xlabel('Fitness')
    plt.ylabel('Número de Individuos')
    plt.title('Distribución del Fitness en la Última Generación')
    plt.tight_layout()
    plt.show()

# Aquí continúa tu código de Tkinter para la interfaz


def mutar_individuo(individuo, prob_mutacion_gen):
    return [mutar_gen(gen, prob_mutacion_gen) for gen in individuo]

def mutar_gen(gen, prob_mutacion_gen):
    if random.random() < prob_mutacion_gen:
        return 1 - gen  # Negación del bit
    else:
        return gen

def podar_poblacion(poblacion_con_fitness, tamano_maximo):
    # Asegurarse de mantener al mejor individuo
    mejor_individuo = max(poblacion_con_fitness, key=lambda item: item[1])
    
    # Eliminar individuos al azar si la población excede el tamaño máximo
    while len(poblacion_con_fitness) > tamano_maximo:
        poblacion_con_fitness.pop(random.randint(0, len(poblacion_con_fitness) - 1))
    
    # Reinsertar el mejor individuo si fue eliminado
    if mejor_individuo not in poblacion_con_fitness:
        poblacion_con_fitness.append(mejor_individuo)

    # Regresar solo los individuos sin el valor de fitness
    return [individuo for individuo, _ in poblacion_con_fitness]



# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Algoritmo Genético")

# Crear y colocar etiquetas y campos de entrada
etiquetas = ["Ingrese la fórmula", "Ingrese la resolución deseable", "Ingrese la probabilidad de mutación del gen",
             "Ingrese la población inicial", "Ingrese la probabilidad de cruza", "Ingrese la población máxima",
             "Ingrese la probabilidad de mutación del individuo", "Ingrese el número de iteraciones"]

entradas = {}

for i, etiqueta in enumerate(etiquetas):
    tk.Label(ventana, text=etiqueta).grid(row=i, column=0)
    entrada = tk.Entry(ventana)
    entrada.grid(row=i, column=1, columnspan=2)
    entradas[etiqueta] = entrada

# Intervalo
tk.Label(ventana, text="Ingrese el intervalo").grid(row=len(etiquetas), column=0)
intervalo_inferior = tk.Entry(ventana)
intervalo_inferior.grid(row=len(etiquetas), column=1)
entradas["Intervalo Inferior"] = intervalo_inferior

intervalo_superior = tk.Entry(ventana)
intervalo_superior.grid(row=len(etiquetas), column=2)
entradas["Intervalo Superior"] = intervalo_superior

# Botón de Maximizar
tk.Button(ventana, text="Maximizar", command=lambda: iniciar_proceso("maximizar")).grid(row=len(etiquetas) + 1, column=0)

# Botón de Minimizar
tk.Button(ventana, text="Minimizar", command=lambda: iniciar_proceso("minimizar")).grid(row=len(etiquetas) + 1, column=1)

# Botón de Salir
tk.Button(ventana, text="Salir", command=ventana.quit).grid(row=len(etiquetas) + 2, column=0)

# Iniciar el loop de la interfaz
ventana.mainloop()