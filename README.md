# REA Emociones
## Generalidades
Este repositiorio contiene los códigos fuentes para la ejecución de la captura de emociones durante la evaluación de un REA en un estudiante.
Dentro de la carpeta "src" se encuentra el archivo "requirements.txt" para instalar las dependencias necesarias a fin de ejecutar los modelos de emociones y parpadeos. A continuación se listan los requisitos generales de sistema.
## Requisitos
* Python >= 3.6
* Navegador Mozilla o Chromium
## Conjunto de datos
Además de lo anterior, se presenta un conjunto de datos de 105 estudiantes anonimizado. En el se presentan las siguientes metricas:
| Nombre                     | Tipo  | Rango                                                 | Descripción                                 |
|----------------------------|-------|-------------------------------------------------------|---------------------------------------------|
| id                         | int   | [0,n]                                                 | Identificador único de la sesión            |
| ang                        | float | [0.0,1.0]                                             | Índice de enojo                             |
| dis                        | float | [0.0,1.0]                                             | Índice de disgusto                          |
| fea                        | float | [0.0,1.0]                                             | Índice de susto                             |
| hap                        | float | [0.0,1.0]                                             | Índice de felicidad                         |
| neu                        | float | [0.0,1.0]                                             | Índice de neutralidad                       |
| sad                        | float | [0.0,1.0]                                             | Índice de tristeza                          |
| sur                        | float | [0.0,1.0]                                             | Índice de sorpresa                          |
| rate_open_eye (blink_rate) | float | [0.0,1.0]                                             | Tasa de apertura                            |
| xp (head_position)         | float | [-5.0,5.0]                                            | Posición de la cabeza en x                  |
| yp (head_position)         | float | [-5.0,5.0]                                            | Posición de la cabeza en y                  |
| is_engagement              | float | [0.0,1.0]                                             | Índice de compromiso                        |
| rea_pos                    | char  | {I: introducción, A: actividad, R: resumen, T: tarea} | Posición del REA                            |
| rea_action                 | char  | {v: video, t: escritura, -: lectura}                  | Acción en el REA                            |
| rea_media                  | float | [0.0,1.0]                                             | Índice de entropía en un componente del REA |
| score_emotion              | float | [0.0,1.0]                                             | Puntaje emocional                           |


