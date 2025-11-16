import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageTk, ImageOps

CANVAS_SIZE = 140
IMAGE_SIZE = 140
TRAIN_PER_SHAPE = 50

# фигуры для обучения
SHAPES = [
    "Круг", "Овал горизонтальный", "Овал вертикальный",
    "Квадрат", "Ромб",
    "Треугольник вверх", "Треугольник вниз",
    "Треугольник вправо", "Треугольник влево",
    "Прямоугольник горизонтальный", "Прямоугольник вертикальный"
]

# генерация обучающих изображений
def generate_shape_series(shape_name):
    images = []

    canvas_area = IMAGE_SIZE * IMAGE_SIZE
    min_area = canvas_area / 6
    max_area = canvas_area * 0.9
    areas = np.linspace(min_area, max_area, TRAIN_PER_SHAPE)
    line_width = 4

    for area in areas:
        img = Image.new("L", (IMAGE_SIZE, IMAGE_SIZE), 0)
        draw = ImageDraw.Draw(img)
        cx, cy = IMAGE_SIZE // 2, IMAGE_SIZE // 2

        if shape_name == "Круг":
            r = int(np.sqrt(area / np.pi))
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=line_width)

        elif shape_name == "Овал горизонтальный":
            a = int(np.sqrt(area / np.pi) * 1.3)
            b = int(np.sqrt(area / np.pi) * 0.7)
            draw.ellipse((cx - a, cy - b, cx + a, cy + b), outline=255, width=line_width)

        elif shape_name == "Овал вертикальный":
            a = int(np.sqrt(area / np.pi) * 0.7)
            b = int(np.sqrt(area / np.pi) * 1.3)
            draw.ellipse((cx - a, cy - b, cx + a, cy + b), outline=255, width=line_width)

        elif shape_name == "Квадрат":
            s = int(np.sqrt(area) / 2)
            draw.rectangle((cx - s, cy - s, cx + s, cy + s), outline=255, width=line_width)

        elif shape_name == "Ромб":
            d = int(np.sqrt(area) / 2)
            pts = [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]
            draw.polygon(pts, outline=255, width=line_width)

        elif "Треугольник" in shape_name:
            s = int(np.sqrt(4 * area / np.sqrt(3)) / 4)
            h = int(np.sqrt(3) * s)
            if "вверх" in shape_name:
                pts = [(cx, cy - h // 2), (cx - s, cy + h // 2), (cx + s, cy + h // 2)]
            elif "вниз" in shape_name:
                pts = [(cx, cy + h // 2), (cx - s, cy - h // 2), (cx + s, cy - h // 2)]
            elif "вправо" in shape_name:
                pts = [(cx + h // 2, cy), (cx - h // 2, cy - s), (cx - h // 2, cy + s)]
            else:
                pts = [(cx - h // 2, cy), (cx + h // 2, cy - s), (cx + h // 2, cy + s)]
            draw.polygon(pts, outline=255, width=line_width)

        elif "Прямоугольник горизонтальный" == shape_name:
            w = int(np.sqrt(area * 1.5))
            h = int(w / 2)
            draw.rectangle((cx - w//2, cy - h//2, cx + w//2, cy + h//2), outline=255, width=line_width)

        elif "Прямоугольник вертикальный" == shape_name:
            h = int(np.sqrt(area * 1.5))
            w = int(h / 2)
            draw.rectangle((cx - w//2, cy - h//2, cx + w//2, cy + h//2), outline=255, width=line_width)

        arr = np.array(img)
        bin_arr = (arr > 128).astype(np.uint8)
        images.append(bin_arr)

    return images


# метод потенциальных функций
def hamming_distance(a, b):
    return np.sum(a != b)

def potential(R):
    return 1_000_000 / (1 + R ** 2)

def recognize(input_img):
    potentials = {}
    distances = {}
    for shape in SHAPES:
        dists = [hamming_distance(input_img, img) for img in train_data[shape]]
        distances[shape] = dists
        potentials[shape] = sum(potential(R) for R in dists)
    recognized = max(potentials, key=potentials.get)
    return recognized, distances, potentials

# статистика
def update_stats(is_correct):
    global total_attempts, correct_attempts
    total_attempts += 1
    if is_correct:
        correct_attempts += 1
    accuracy = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    stat_label.config(text=f"Угадано: {correct_attempts}/{total_attempts}\nТочность: {accuracy:.1f}%")

# рисование
def draw(event):
    x, y = event.x, event.y
    r = 2
    canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black")
    draw_img.ellipse([x - r, y - r, x + r, y + r], fill=255)

def clear_canvas():
    canvas.delete("all")
    draw_img.rectangle([0, 0, CANVAS_SIZE, CANVAS_SIZE], fill=0)
    dist_text.delete(1.0, tk.END)

# распознавание
def recognize_shape():
    img_arr = np.array(image)
    img_bin = (img_arr > 128).astype(np.uint8)

    ys, xs = np.where(img_bin > 0)
    if len(xs) == 0 or len(ys) == 0:
        messagebox.showwarning("Ошибка", "Нарисуйте фигуру перед распознаванием!")
        return

    # выделение фигуры
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()
    cropped = img_bin[y_min:y_max + 1, x_min:x_max + 1]

    # масштабирование и центрирование в поле IMAGE_SIZE x IMAGE_SIZE
    cropped_img = Image.fromarray(cropped * 255)
    scaled_img = ImageOps.pad(
        cropped_img,
        (IMAGE_SIZE, IMAGE_SIZE),
        color=0,
        centering=(0.5, 0.5)
    )
    centered = (np.array(scaled_img) > 128).astype(np.uint8)

    recognized, distances, potentials = recognize(centered)

    # вывод потенциалов
    dist_text.delete(1.0, tk.END)
    for shape in SHAPES:
        dist_text.insert(tk.END, f"{shape}:\n  Потенциал: {potentials[shape]:.2f}\n\n")

    # группировка по категориям
    if "Треугольник" in recognized:
        question = "Это треугольник?"
    elif "Прямоугольник" in recognized:
        question = "Это прямоугольник?"
    elif "Овал" in recognized:
        question = "Это овал?"
    else:
        question = f"Это {recognized.lower()}?"

    result = messagebox.askyesno("Результат", question)
    update_stats(result)

# интерфейс
root = tk.Tk()
root.title("Распознавание фигур методом потенциальных функций")

frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)

frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(frame_left, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white", borderwidth=2, relief="solid")
canvas.pack()

image = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), 0)
draw_img = ImageDraw.Draw(image)
canvas.bind("<B1-Motion>", draw)

btn_recognize = tk.Button(frame_left, text="Распознать", command=recognize_shape, width=20)
btn_recognize.pack(pady=5)

btn_clear = tk.Button(frame_left, text="Очистить", command=clear_canvas, width=20)
btn_clear.pack(pady=5)

stat_label = tk.Label(frame_right, text="Угадано: 0/0\nТочность: 0%", font=("Arial", 12), justify="left")
stat_label.pack(anchor="nw")

dist_text = tk.Text(frame_right, width=45, height=25, font=("Consolas", 10))
dist_text.pack(fill=tk.BOTH, expand=True)

# обучение
train_data = {shape: generate_shape_series(shape) for shape in SHAPES}
total_attempts = 0
correct_attempts = 0

root.mainloop()
