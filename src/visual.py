import cv2
import numpy as np

from constants import colors


def chart_bar(prediction, dim, classes):
    h, _, z = dim
    size = (h,300,z)
    heigth = 150
    width = 200
    canvas = np.full(size, 25, dtype=np.uint8)

    y0 = h//2 - (heigth//2)

    for i, intensity in enumerate(prediction):
        x1 = int(width * intensity)
        x2 = width
        y1 = i * (heigth//7) + y0
        y2 = (i + 1) * (heigth//7) + y0
        cv2.rectangle(canvas, (x1,y1), (x2,y2), (100,100,100), -1)
        cv2.putText(canvas, f'{ classes[i] }', (width, y1 + (y2 - y1)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 1)
        cv2.putText(canvas, f'{ round(float(intensity), 2) }', (x1, y1 + (y2 - y1)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 1)

    return canvas

def chart_plot(lines, dim, classes, new_values):
    _, w, z = dim
    h = 100
    size = (h,w,z)
    canvas = np.zeros(size, dtype=np.uint8)
    
    for i, _ in enumerate(new_values):
        lines[i,:-1] = lines[i,1:]
        lines[i,-1] = new_values[i]

    step = w/lines[0].shape[0]

    for j, _ in enumerate(new_values):
        for i in range(1, lines[j].shape[0]):
            cv2.line(canvas, (int((i - 1) * step), h - int(lines[j,i-1] * h)), (int(i * step), h - int(lines[j,i] * h)), colors[j], 1)

    return canvas, lines