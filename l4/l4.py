import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageTk

CANVAS_SIZE = 70
IMAGE_SIZE = 70
SHAPES = ["Круг", "Квадрат", "Треугольник"]
TRAIN_PER_SHAPE = 5

# фигуры для обучения
def generate_shape_series(shape_name):
    images = []
    target_area = 550  # целевая площадь в пикселях
    variations = np.linspace(-0.2, 0.2, TRAIN_PER_SHAPE)  # разброс

    for var in variations:
        img = Image.new("L", (IMAGE_SIZE, IMAGE_SIZE), 0)
        draw = ImageDraw.Draw(img)
        cx, cy = IMAGE_SIZE // 2, IMAGE_SIZE // 2

        if shape_name == "Круг":
            area = target_area * (1 + var)
            r = int(np.sqrt(area / np.pi))
            r = np.clip(r, 5, IMAGE_SIZE // 2 - 2)
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)

        elif shape_name == "Квадрат":
            area = target_area * (1 + var)
            s = int(np.sqrt(area) / 2)
            s = np.clip(s, 5, IMAGE_SIZE // 2 - 2)
            draw.rectangle((cx - s, cy - s, cx + s, cy + s), fill=255)

        elif shape_name == "Треугольник":
            area = target_area * (1 + var)
            s = int(np.sqrt(area / np.sqrt(3)))
            s = np.clip(s, 5, IMAGE_SIZE // 2 - 4)
            h = int(np.sqrt(3) * s)
            pts = [
                (cx, cy - h // 2),
                (cx - s, cy + h // 2),
                (cx + s, cy + h // 2)
            ]
            draw.polygon(pts, fill=255)

        # преобразование в бинарный массив
        arr = np.array(img)
        bin_arr = (arr > 128).astype(np.uint8)
        images.append(bin_arr)

    return images

# метод потенциальных функций
def hamming_distance(a, b):
    return np.sum(a != b)

def potential(R):
    return 1_000_000 / (1 + R ** 2)

def recognize(test_img):
    potentials = {}
    distances = {}
    for shape in SHAPES:
        dists = [hamming_distance(test_img, img) for img in train_data[shape]]
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
    stat_label.config(text=f"✅ Угадано: {correct_attempts}/{total_attempts}\nТочность: {accuracy:.1f}%")

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
    # Получаем изображение с холста
    large_img = image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.NEAREST)  # ← без сглаживания!
    large_arr = np.array(large_img)
    test_bin = (large_arr > 128).astype(np.uint8)

    # Распознавание без центрирования
    recognized, distances, potentials = recognize(test_bin)

    # вывод результатов
    dist_text.delete(1.0, tk.END)
    for shape in SHAPES:
        dist_text.insert(tk.END, f"{shape}:\n")
        dist_text.insert(tk.END, f"  Расстояния: {distances[shape]}\n")
        dist_text.insert(tk.END, f"  Потенциал: {potentials[shape]:.2f}\n\n")

    # запрос подтверждения
    result = messagebox.askyesno("Результат", f"Это {recognized}?")
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

btn_recognize = tk.Button(frame_left, text="Распознать", command=recognize_shape, width=20, bg="#90ee90")
btn_recognize.pack(pady=5)

btn_clear = tk.Button(frame_left, text="Очистить", command=clear_canvas, width=20, bg="#ffcccb")
btn_clear.pack(pady=5)

stat_label = tk.Label(frame_right, text="✅ Угадано: 0/0\nТочность: 0%", font=("Arial", 12), justify="left")
stat_label.pack(anchor="nw")

dist_text = tk.Text(frame_right, width=45, height=20, font=("Consolas", 10))
dist_text.pack(fill=tk.BOTH, expand=True)

# генерация обучающей выборки
train_data = {shape: generate_shape_series(shape) for shape in SHAPES}
total_attempts = 0
correct_attempts = 0

root.mainloop()
