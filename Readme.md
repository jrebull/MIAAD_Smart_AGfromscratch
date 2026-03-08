Materia: Optimización Inteligente
Profesor: Mtro. Raul Gibran Porras Alaniz

Universidad: Universidad Autónoma de Ciudad Juárez (UACJ)

Maestria: Maestría en Inteligencia Artificial y Analítica de Datos (MIAAD)

Actividad: Análisis de Rendimiento de un Algoritmo Genético para el VRP

Fecha de Entrega: 08 de marzo de 2026

Matricula de Alumno: 263483
Alumno: Javier Augusto Rebull Saucedo


Objetivo de la Práctica:
El objetivo de esta actividad es que comprendan la mecánica interna de las metaheurísticas evolutivas y analicen su comportamiento ante diferentes escenarios de un mismo problema. Comprobarán cómo un modelo de optimización general y bien estructurado puede adaptarse y resolver diversas instancias operativas únicamente ajustando las características y parámetros del problema.

🛠️ Fase 1: Replicación del Modelo Base
En la sección de Recursos de esta semana, encontrarán un archivo llamado AGfromscratch.html

Nota importante: Deben descargar este archivo a sus computadoras y abrirlo directamente con su navegador web (Chrome, Edge, Safari, etc.) para que las ecuaciones matemáticas y el formato de código (estilo IDE) se visualicen de manera correcta.

Basándose en la explicación detallada de ese documento, deberán replicar el modelo en Python creando dos scripts separados:

generador_instancias.py: Para crear los escenarios de prueba.

ag_vrp.py: El motor de la metaheurística.

🔬 Fase 2: Experimentación y Escenarios de Prueba
Una vez que su algoritmo base funcione correctamente, diseñarán un experimento computacional. Deberán someter a su Algoritmo Genético a las siguientes pruebas de estrés y escalabilidad:

Escenario 1 (Escalabilidad Media): Generar una instancia con 100 clientes.

Escenario 2 (Alta Escalabilidad): Generar una instancia con 200 clientes.

Escenario 3 (Variabilidad Económica): Modificar los rangos aleatorios de "Demanda" y "Valor por unidad" en el generador de instancias para simular un mercado diferente.

Escenario 4 y 5 (Estrés Operativo): Realizar dos pruebas adicionales donde modifiquen los parámetros de penalización (costo de vehículo, costo por km, penalización por espacio vacío) y la capacidad máxima de los vehículos.

📊 Fase 3: Metodología de Ejecución y Métricas
Dado el carácter estocástico (aleatorio) de los Algoritmos Genéticos, una sola ejecución no tiene validez estadística. Por lo tanto, para cada uno de los escenarios planteados, deberán ejecutar el algoritmo 30 veces de manera independiente.

Para cada escenario, deberán registrar y calcular las siguientes métricas de rendimiento:

Mejor Ganancia (Best Fitness): El valor de la función objetivo (Z) más alto encontrado en las 30 ejecuciones. Este fungirá como su "Óptimo Conocido" o "Best Known Solution" (BKS) para esa instancia.

Promedio de la Mejor Ganancia (Average Best Fitness): La media aritmética de los mejores resultados obtenidos en las 30 ejecuciones.

Brecha (Gap): La diferencia porcentual promedio entre los resultados obtenidos y su Óptimo Conocido.

Tasa de Éxito (Success Rate): El porcentaje de veces (de las 30 ejecuciones) que el algoritmo logró encontrar o acercarse al Óptimo Conocido (pueden definir un margen de tolerancia del 1% o 2%).

📝 Entregable
Deberán subir a la plataforma un Reporte Técnico en formato PDF que contenga:

Una breve introducción al problema.

El diseño de sus experimentos (qué valores exactos utilizaron para los escenarios 3, 4 y 5).

Tablas comparativas con las 4 métricas de rendimiento exigidas para cada escenario.

Hallazgos y Conclusiones: Un análisis crítico sobre cómo se degradó o mantuvo el rendimiento del algoritmo al aumentar la dimensionalidad (100 vs 200 clientes) y cómo los cambios en las penalizaciones afectaron la estructura de las rutas generadas.
