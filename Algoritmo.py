import tkinter as tk
from tkinter import ttk
import random
import itertools
import math
import matplotlib.pyplot as plt


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

def evaluar_fitness(individuo, intervalo_inferior, intervalo_superior):
    """Evalúa el fitness de un individuo usando la función dada."""
    x = binario_a_decimal(individuo, intervalo_inferior, intervalo_superior)
    return ((x * 3) * math.sin(x)) / 100 + (x * 2) * math.cos(x)

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


def mostrar_resultados(poblacion_con_fitness, intervalo_inferior, intervalo_superior):
    # Crear una nueva ventana
    ventana_resultados = tk.Toplevel()
    ventana_resultados.title("Resultados de la Última Generación")

    # Crear un Treeview
    tree = ttk.Treeview(ventana_resultados, columns=('Cromosoma', 'Fenotipo', 'Fitness'), show='headings')
    tree.heading('Cromosoma', text='Cromosoma')
    tree.heading('Fenotipo', text='Fenotipo')
    tree.heading('Fitness', text='Fitness')
    tree.grid(row=0, column=0, sticky='nsew')

    # Agregar datos a la tabla
    for individuo, fitness in poblacion_con_fitness:
        fenotipo = binario_a_decimal(individuo, intervalo_inferior, intervalo_superior)
        tree.insert('', tk.END, values=(str(individuo), f"{fenotipo:.2f}", f"{fitness:.2f}"))



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
            if random.random() < prob_cruza:  # Aplicar la probabilidad de cruza
                punto_cruza = random.randint(1, len(ind1) - 1)
                descendiente1, descendiente2 = cruzar_en_punto_fijo(ind1, ind2, punto_cruza)
                nueva_poblacion.extend([descendiente1, descendiente2])
            else:
                # Si no se realiza el cruzamiento, pasar los individuos sin cambios
                nueva_poblacion.extend([ind1, ind2])

        # Mutación
        nueva_poblacion = [mutar_individuo(ind, prob_mutacion_gen) if random.random() < prob_mutacion_individuo else ind for ind in nueva_poblacion]

        # Evaluación de fitness y poda
        poblacion_con_fitness = [(ind, evaluar_fitness(ind, intervalo_inferior, intervalo_superior)) for ind in nueva_poblacion]
        
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
    
    mostrar_resultados(poblacion_con_fitness, intervalo_inferior, intervalo_superior)



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



# Estilos
COLOR_FONDO = "#f0f0f0"
COLOR_BOTON = "#d9d9d9"
FUENTE = ("Arial", 10)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Algoritmo Genético")
ventana.configure(bg=COLOR_FONDO)

# Crear y colocar etiquetas y campos de entrada
etiquetas = ["Ingrese la resolución deseable", "Ingrese la probabilidad de mutación del gen",
             "Ingrese la población inicial", "Ingrese la probabilidad de cruza", "Ingrese la población máxima",
             "Ingrese la probabilidad de mutación del individuo", "Ingrese el número de iteraciones"]

# Fórmula fija
etiqueta_formula = "Fórmula: ((3x) ⋅ sen(x)) / 100 + (2x) ⋅ cos(x)"
tk.Label(ventana, text=etiqueta_formula, wraplength=300, bg=COLOR_FONDO, font=FUENTE).grid(row=0, column=0, columnspan=3)

entradas = {}

# Crear Frame para entradas
frame_entradas = tk.Frame(ventana, bg=COLOR_FONDO)
frame_entradas.grid(row=1, column=0, columnspan=3, sticky="ew")

# Crear campos de entrada para las etiquetas
for i, etiqueta in enumerate(etiquetas):
    tk.Label(frame_entradas, text=etiqueta, bg=COLOR_FONDO, font=FUENTE).grid(row=i, column=0, sticky="w")
    entrada = tk.Entry(frame_entradas, font=FUENTE)
    entrada.grid(row=i, column=1, columnspan=2, sticky="ew")
    entradas[etiqueta] = entrada

# Intervalo
frame_intervalo = tk.Frame(ventana, bg=COLOR_FONDO)
frame_intervalo.grid(row=2, column=0, columnspan=3, sticky="ew")

tk.Label(frame_intervalo, text="Intervalo Inferior", bg=COLOR_FONDO, font=FUENTE).grid(row=0, column=0)
intervalo_inferior = tk.Entry(frame_intervalo, font=FUENTE)
intervalo_inferior.grid(row=0, column=1)
entradas["Intervalo Inferior"] = intervalo_inferior

tk.Label(frame_intervalo, text="Intervalo Superior", bg=COLOR_FONDO, font=FUENTE).grid(row=0, column=2)
intervalo_superior = tk.Entry(frame_intervalo, font=FUENTE)
intervalo_superior.grid(row=0, column=3)
entradas["Intervalo Superior"] = intervalo_superior

# Botones
frame_botones = tk.Frame(ventana, bg=COLOR_FONDO)
frame_botones.grid(row=3, column=0, columnspan=3, sticky="ew")

tk.Button(frame_botones, text="Maximizar", bg=COLOR_BOTON, font=FUENTE, command=lambda: iniciar_proceso("maximizar")).grid(row=0, column=0)
tk.Button(frame_botones, text="Minimizar", bg=COLOR_BOTON, font=FUENTE, command=lambda: iniciar_proceso("minimizar")).grid(row=0, column=1)
tk.Button(frame_botones, text="Salir", bg=COLOR_BOTON, font=FUENTE, command=ventana.quit).grid(row=0, column=2)

# Configuración de columnas para que se expandan adecuadamente
frame_entradas.columnconfigure(1, weight=1)
frame_intervalo.columnconfigure([1, 3], weight=1)
frame_botones.columnconfigure([0, 1, 2], weight=1)

# Iniciar el loop de la interfaz
ventana.mainloop()