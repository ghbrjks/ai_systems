import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

perceptron_weights = None
perceptron_thresholds = None
user_points = []
user_stats = {
    "total": 0,
    "correct": 0,
    "details": []
}

def normalize_coordinates(coords):
    x, y, z = coords
    length = np.sqrt(x*x + y*y + z*z)
    if length > 0:
        return [x/length, y/length, z/length]
    return [0, 0, 0]

def get_octant_label(x, y, z):
    if x >= 0:
        if y >= 0:
            if z >= 0:
                return 0
            else:
                return 4
        else:
            if z >= 0:
                return 3
            else:
                return 7
    else:
        if y >= 0:
            if z >= 0:
                return 1
            else:
                return 5
        else:
            if z >= 0:
                return 2
            else:
                return 6

def generate_training_data(num_points_per_octant=10, seed=42):
    random.seed(seed)
    training_data = []
    
    for octant_idx in range(8):
        for _ in range(num_points_per_octant):
            x_sign = 1 if octant_idx in [0, 3, 4, 7] else -1
            y_sign = 1 if octant_idx in [0, 1, 4, 5] else -1
            z_sign = 1 if octant_idx in [0, 1, 2, 3] else -1
            
            if x_sign > 0:
                x_coord = random.uniform(0.1, 10.0)
            else:
                x_coord = random.uniform(-10.0, -0.1)
                
            if y_sign > 0:
                y_coord = random.uniform(0.1, 10.0)
            else:
                y_coord = random.uniform(-10.0, -0.1)
                
            if z_sign > 0:
                z_coord = random.uniform(0.1, 10.0)
            else:
                z_coord = random.uniform(-10.0, -0.1)
            
            normalized_coords = normalize_coordinates([x_coord, y_coord, z_coord])
            
            target = [0] * 8
            target[octant_idx] = 1
            
            training_data.append((normalized_coords, target))
    
    return training_data

def generate_test_data(seed=89):
    random.seed(seed)
    test_data = []
    graph_data = []
    points_per_octant = 4
            
    for octant_idx in range(8):
        for _ in range(points_per_octant):
            x_sign = 1 if octant_idx in [0, 3, 4, 7] else -1
            y_sign = 1 if octant_idx in [0, 1, 4, 5] else -1
            z_sign = 1 if octant_idx in [0, 1, 2, 3] else -1
            
            if x_sign > 0:
                x_coord = random.uniform(0.1, 10.0)
            else:
                x_coord = random.uniform(-10.0, -0.1)
                
            if y_sign > 0:
                y_coord = random.uniform(0.1, 10.0)
            else:
                y_coord = random.uniform(-10.0, -0.1)
                
            if z_sign > 0:
                z_coord = random.uniform(0.1, 10.0)
            else:
                z_coord = random.uniform(-10.0, -0.1)
            
            normalized_coords = normalize_coordinates([x_coord, y_coord, z_coord])
            
            graph_coords = [x_coord, y_coord, z_coord]
            graph_data.append(graph_coords)

            target = get_octant_label(x_coord, y_coord, z_coord)
            test_data.append((normalized_coords, target))
    
    return test_data, graph_data

def activate(net, thresholds):
    out = np.zeros_like(net)
    out[net > thresholds] = 1
    return out

def predict(inputs, weights, thresholds):
    inputs = np.array(inputs)
    net = np.dot(inputs, weights)
    output = activate(net, thresholds)

    active_neurons = np.where(output == 1)[0]
    if len(active_neurons) == 1:
        return active_neurons[0]
    elif len(active_neurons) == 0:
        return -1
    else:
        return active_neurons[0]


def train_perceptron(training_data, num_inputs=3, num_outputs=8, learning_rate=1, epochs=2000):
    # 1. Инициализация весов и порогов
    weights = np.random.uniform(low=-0.5, high=0.5, size=(num_inputs, num_outputs))
    thresholds = np.random.uniform(low=-0.5, high=0.5, size=(num_outputs,))
    
    for epoch in range(epochs):
        total_error = 0
        for input_vector, target_vector in training_data:
            # 2. Вычисление NET
            inputs = np.array(input_vector)
            target = np.array(target_vector)
            
            net = np.dot(inputs, weights)
            
            # 3. Вычисление OUT
            output = activate(net, thresholds)
            
            # 4. Вычисление ошибки
            error = target - output
            total_error += np.sum(np.abs(error))

            # 5. Коррекция весов
            weight_update = learning_rate * np.outer(inputs, error)
            weights += weight_update
            
            # Коррекция порогов
            threshold_update = -learning_rate * error
            thresholds += threshold_update

        if total_error == 0:
            print(f"Обучение завершено на эпохе {epoch+1} (ошибка = {total_error})")
            break
    print(f"Обучение завершено на эпохе {epochs} (ошибка = {total_error})")
    
    return weights, thresholds


def on_submit_point(entry_x, entry_y, entry_z, ax, canvas, stats_text):
    global perceptron_weights, perceptron_thresholds, user_points, user_stats
    
    try:
        x = float(entry_x.get())
        y = float(entry_y.get())
        z = float(entry_z.get())
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Пожалуйста, введите числовые значения для X, Y, Z.")
        return

    normalized_inputs = normalize_coordinates([x, y, z])
    
    # предсказание
    predicted_octant = predict(normalized_inputs, perceptron_weights, perceptron_thresholds)
    true_octant = get_octant_label(x, y, z)
    is_correct = (predicted_octant == true_octant and predicted_octant != -1)

    user_points.append(([x, y, z], predicted_octant))
    user_stats["total"] += 1
    if is_correct:
        user_stats["correct"] += 1

    point_color = 'green' if is_correct else 'red'

    ax.scatter(x, y, z, c=point_color, s=50, label=f'{"Угадано" if is_correct else "Не угадано"}')
    canvas.draw()

    result_str = f"Угадано" if is_correct else f"Не угадано (предсказано: {predicted_octant}, правильный: {true_octant})"
    detail_str = f"Точка ({x:.2f}, {y:.2f}, {z:.2f}): {result_str}\n"
    user_stats["details"].append(detail_str)

    accuracy = (user_stats["correct"] / user_stats["total"]) * 100 if user_stats["total"] > 0 else 0

    stats_text.config(state=tk.NORMAL)
    stats_text.delete(1.0, tk.END)
    stats_text.insert(tk.END, f"Всего точек: {user_stats['total']}\n")
    stats_text.insert(tk.END, f"Правильно угадано: {user_stats['correct']}\n")
    stats_text.insert(tk.END, f"Неправильно: {user_stats['total'] - user_stats['correct']}\n")
    stats_text.insert(tk.END, f"Точность: {accuracy:.2f}%\n\n")
    stats_text.insert(tk.END, "Детали:\n")
    for detail in user_stats["details"][-10:]:
         stats_text.insert(tk.END, detail)
    stats_text.config(state=tk.DISABLED)


def main():
    global perceptron_weights, perceptron_thresholds, user_points, user_stats
    
    print("Генерация обучающей выборки...")
    training_data = generate_training_data(num_points_per_octant=10)
    print(f"Обучающая выборка: {len(training_data)} точек.")

    print("\nСоздание и обучение персептрона...")
    perceptron_weights, perceptron_thresholds = train_perceptron(training_data, learning_rate=1.0, epochs=2000)
    print(f"\nОбученные веса:\n{perceptron_weights}")
    print(f"Обученные пороги:\n{perceptron_thresholds}")

    print("\nГенерация тестовой выборки...")
    test_data = generate_test_data()
    print(f"Тестовая выборка: {len(test_data[0])} точек.")

    print("\nТестирование персептрона...")
    correct_predictions = 0
    total_predictions = len(test_data[0])
    for input_coords, true_octant in test_data[0]:
        predicted_octant = predict(input_coords, perceptron_weights, perceptron_thresholds)
        if predicted_octant == true_octant and predicted_octant != -1:
            correct_predictions += 1
    accuracy = (correct_predictions / total_predictions) * 100
    print(f"Точность на тестовой выборке: {accuracy:.2f}%")

    root = tk.Tk()
    root.title("Персептрон: Случайные точки")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    left_frame = ttk.Frame(main_frame, width=300)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 5), pady=5)
    left_frame.pack_propagate(False)

    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

    title_label = ttk.Label(left_frame, text="Классификация точки", font=("Arial", 12, "bold"))
    title_label.pack(pady=(0, 10))

    input_frame = ttk.Frame(left_frame)
    input_frame.pack(fill=tk.X, pady=5)

    ttk.Label(input_frame, text="X:").grid(row=0, column=0, sticky=tk.W)
    entry_x = ttk.Entry(input_frame, width=10)
    entry_x.grid(row=0, column=1, padx=(5, 0))
    entry_x.insert(0, "0.0")

    ttk.Label(input_frame, text="Y:").grid(row=1, column=0, sticky=tk.W)
    entry_y = ttk.Entry(input_frame, width=10)
    entry_y.grid(row=1, column=1, padx=(5, 0))
    entry_y.insert(0, "0.0")

    ttk.Label(input_frame, text="Z:").grid(row=2, column=0, sticky=tk.W)
    entry_z = ttk.Entry(input_frame, width=10)
    entry_z.grid(row=2, column=1, padx=(5, 0))
    entry_z.insert(0, "0.0")

    submit_button = ttk.Button(left_frame, text="Добавить точку", command=lambda: on_submit_point(entry_x, entry_y, entry_z, ax, canvas, stats_text))
    submit_button.pack(pady=10)

    stats_frame = ttk.LabelFrame(left_frame, text="Статистика пользовательских точек")
    stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    stats_text = tk.Text(stats_frame, height=10, state=tk.DISABLED)
    stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Визуализация пользовательских точек')
    lim = 10
    ax.set_xlim([-lim, lim])
    ax.set_ylim([-lim, lim])
    ax.set_zlim([-lim, lim])
    ax.plot([-lim, lim], [0, 0], [0, 0], color='k', linestyle='--', alpha=0.5)
    ax.plot([0, 0], [-lim, lim], [0, 0], color='k', linestyle='--', alpha=0.5)
    ax.plot([0, 0], [0, 0], [-lim, lim], color='k', linestyle='--', alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    for point in test_data[1]:
        normalized_input = normalize_coordinates(point)
        predicted_octant = predict(normalized_input, perceptron_weights, perceptron_thresholds)
        x,y,z = point
        if predicted_octant == 0:
            ax.scatter(x, y, z, c='yellow', s=50)
        elif predicted_octant == 1:
            ax.scatter(x, y, z, c='red', s=50)
        elif predicted_octant == 2:
            ax.scatter(x, y, z, c='green', s=50)
        elif predicted_octant == 3:
            ax.scatter(x, y, z, c='blue', s=50)
        elif predicted_octant == 4:
            ax.scatter(x, y, z, c='black', s=50)
        elif predicted_octant == 5:
            ax.scatter(x, y, z, c='pink', s=50)
        elif predicted_octant == 6:
            ax.scatter(x, y, z, c='orange', s=50)
        else:
            ax.scatter(x, y, z, c='purple', s=50)
        canvas.draw()

    user_points = []
    user_stats = {
        "total": 0,
        "correct": 0,
        "details": []
    }
    
    info_label = ttk.Label(left_frame, text="* Диапазон координат: от -10 до -0.1 и от 0.1 до 10", 
                          font=("Arial", 8), foreground="gray")
    info_label.pack(pady=(0, 5))
    
    root.mainloop()

if __name__ == "__main__":
    main()