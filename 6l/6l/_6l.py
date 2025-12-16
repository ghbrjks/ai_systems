import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

user_points = []
user_stats = {
    "total": 0,
    "correct": 0,
    "details": []
}

# нормализация
def normalize_vector(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v.copy()
    return v / norm

# поиск победителя
def find_winner(input_vector, weights):
    dot_products = np.dot(weights, input_vector)
    winner_index = np.argmax(dot_products)
    return winner_index

# поиск соответствия между нейронами и классами
def find_neuron_class_assignments(winners, true_labels, n_neurons):
    neuron_assignments = {}
    for neuron_id in range(n_neurons):
        neuron_mask = winners == neuron_id
        if not np.any(neuron_mask):
            neuron_assignments[neuron_id] = None
            continue
        corresponding_classes = true_labels[neuron_mask]
        unique_classes, counts = np.unique(corresponding_classes, return_counts=True)
        assigned_class_idx = unique_classes[np.argmax(counts)]
        neuron_assignments[neuron_id] = assigned_class_idx
    return neuron_assignments

# загрузка датасета
def load_and_preprocess_data():
    iris = load_iris()
    points = iris.data.astype(np.float64)
    true_classes = iris.target
    feature_names = iris.feature_names
    class_names = iris.target_names

    points_normalized = np.zeros_like(points)
    for i in range(points.shape[0]):
        points_normalized[i] = normalize_vector(points[i])

    return points_normalized, true_classes, feature_names, class_names

# запуск обучения
def run_kohonen_training(train_data, n_neurons, total_epochs):
    n_inputs = train_data.shape[1]
    
    chosen_indices = np.random.choice(len(train_data), size=n_neurons, replace=False)
    # weights = np.random.rand(n_neurons, n_inputs).astype(np.float64)
    # for i in range(weights.shape[0]):
    #     weights[i] = normalize_vector(weights[i])
    weights = train_data[chosen_indices].copy().astype(np.float64)
    for i in range(weights.shape[0]):
        weights[i] = normalize_vector(weights[i])
    initial_learning_rate = 0.7
    learning_rates = np.full(n_neurons, initial_learning_rate, dtype=np.float64)

    print(f"Начало обучения сети...")
    print(f"Всего шагов/эпох: {total_epochs}")
    print(f"Размер обучающей выборки: {train_data.shape[0]}")

    for i in range(total_epochs):
        # выбор одного обучающего вектора
        random_sample = train_data[np.random.choice(train_data.shape[0])]

        # поиск победителя
        winner_idx = find_winner(random_sample, weights)

        # обновление весов победителя
        weights[winner_idx] += learning_rates[winner_idx] * (random_sample - weights[winner_idx])
        # обновление коэффициента обучения победителя
        learning_rates[winner_idx] = (total_epochs - i) / 100.0

    print("Обучение завершено.")
    return weights

# вычисление точности
def calculate_accuracy_metrics(final_weights, test_data, test_true_labels):
    winners = []
    for sample in test_data:
        winner_idx = find_winner(sample, final_weights)
        winners.append(winner_idx)
    winners = np.array(winners)

    n_neurons = len(final_weights)
    
    neuron_assignments = find_neuron_class_assignments(winners, test_true_labels, n_neurons)

    total_predictions = len(test_data)
    total_correct = 0

    for i in range(len(test_data)):
        predicted_neuron = winners[i]
        true_class = test_true_labels[i]
        
        assigned_class_for_neuron = neuron_assignments.get(predicted_neuron)
        
        if assigned_class_for_neuron is not None and assigned_class_for_neuron == true_class:
            total_correct += 1

    overall_accuracy = total_correct / total_predictions
    print(f"\nВсего элементов в тестовой выборке: {total_predictions}")
    print(f"Правильно классифицировано: {total_correct}")
    print(f"Общая точность: {overall_accuracy:.2%}")
    
    return overall_accuracy
    
def on_submit_point(entry_x, entry_y, ax2, canvas, true_labels, final_weights, class_names, neuron_assignments, stats_text_widget):
    global user_points, user_stats

    try:
        x = float(entry_x.get())
        y = float(entry_y.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите числовые значения для X и Y.")
        return

    user_input_full = np.zeros(final_weights.shape[1])
    user_input_full[0] = x
    user_input_full[1] = y
    normalized_user_input = normalize_vector(user_input_full)

    user_winner_idx = find_winner(normalized_user_input, final_weights)

    predicted_class_idx = neuron_assignments.get(user_winner_idx, None)

    predicted_class_name = class_names[predicted_class_idx]
    color_map = {name: ['blue', 'orange', 'green'][i] for i, name in enumerate(class_names)}
    point_color = color_map[predicted_class_name]

    ax2.scatter(x, y, c=point_color, s=50, alpha=0.7, zorder=5)

    user_stats["total"] += 1

    correct_answer = messagebox.askyesnocancel(
        "Проверка классификации",
        f"Сеть классифицировала точку ({x:.2f}, {y:.2f}) как '{predicted_class_name}' (Нейрон {user_winner_idx}).\n"
        f"Является ли это правильной классификацией?"
    )

    is_correct = correct_answer
    if is_correct:
        user_stats["correct"] += 1
            
    user_stats["details"].append({
        "coords": (x, y),
        "predicted": predicted_class_name,
        "true_input": None,
        "correct": is_correct
    })

    update_stats_display(stats_text_widget)

    canvas.draw()

   
def update_stats_display(stats_widget):
    stats_widget.config(state=tk.NORMAL)
    stats_widget.delete(1.0, tk.END)

    total = user_stats["total"]
    correct = user_stats["correct"]
    accuracy = (correct / total * 100) if total > 0 else 0

    stats_text = f"Статистика пользовательских точек:\n"
    stats_text += f"Всего точек: {total}\n"
    stats_text += f"Правильно: {correct}\n"
    stats_text += f"Точность: {accuracy:.2f}%\n\n"
    stats_text += "Детали:\n"
    for detail in user_stats["details"]:
        correctness = "Правильно" if detail['correct'] else "Неправильно"
        stats_text += f"  Точка {detail['coords']}: Предсказано '{detail['predicted']}', {correctness}\n"

    stats_widget.insert(tk.END, stats_text)
    stats_widget.config(state=tk.DISABLED)


def main():
    # загрузка данных
    points_norm, true_class, feature_names, target_names = load_and_preprocess_data()

    # параметры сети
    num_neurons = 3
    epochs = 100

    # обучение
    final_weights = run_kohonen_training(points_norm, num_neurons, epochs)

    # вычисление точности
    calculate_accuracy_metrics(final_weights, points_norm, true_class)

    winners = []
    for sample in points_norm:
        winner_idx = find_winner(sample, final_weights)
        winners.append(winner_idx)
    winners = np.array(winners)
    neuron_assignments = find_neuron_class_assignments(winners, true_class, len(final_weights))

    root = tk.Tk()
    root.title("Сеть Кохонена")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    left_frame = ttk.Frame(main_frame, width=300)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 5), pady=5)
    left_frame.pack_propagate(False)

    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

    # левая панель
    title_label = ttk.Label(left_frame, text="Классификация точки", font=("Arial", 12, "bold"))
    title_label.pack(pady=(0, 10))

    input_frame = ttk.Frame(left_frame)
    input_frame.pack(fill=tk.X, pady=5)

    ttk.Label(input_frame, text="Длина лепестка (см):").grid(row=0, column=0, sticky=tk.W)
    entry_x = ttk.Entry(input_frame, width=10)
    entry_x.grid(row=0, column=1, padx=(5, 0))
    entry_x.insert(0, "0.0")

    ttk.Label(input_frame, text="Ширина лепестка (см):").grid(row=1, column=0, sticky=tk.W)
    entry_y = ttk.Entry(input_frame, width=10)
    entry_y.grid(row=1, column=1, padx=(5, 0))
    entry_y.insert(0, "0.0")

    submit_button = ttk.Button(
        left_frame,
        text="Добавить точку",
        command=lambda: on_submit_point(
            entry_x, entry_y, ax2, canvas, true_class, final_weights, target_names, neuron_assignments, stats_text
        )
    )
    submit_button.pack(pady=10)

    # статистика
    stats_frame = ttk.LabelFrame(left_frame, text="Статистика пользовательских точек")
    stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    stats_text = tk.Text(stats_frame, wrap=tk.WORD, state=tk.DISABLED)
    stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    update_stats_display(stats_text)

    # правая панель
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    color_map = {name: ['blue', 'orange', 'green'][i] for i, name in enumerate(target_names)}

    # график 1
    for i, class_name in enumerate(target_names):
        mask = true_class == i
        ax1.scatter(
            points_norm[mask, 0],
            points_norm[mask, 1],
            c=color_map[class_name],
            label=f'{class_name}',
            s=50,
            alpha=0.7
        )
    ax1.set_title('Распределение точек Iris (по истинным меткам)')
    ax1.set_xlabel(feature_names[0])
    ax1.set_ylabel(feature_names[1])
    ax1.legend(loc='upper left')

    # график 2
    legend_elements = []
    for neuron_id in range(len(final_weights)):
        if neuron_assignments[neuron_id] is None:
            continue
        mask = winners == neuron_id
        dominant_class_idx = neuron_assignments[neuron_id]
        dominant_class_name = target_names[dominant_class_idx]
        color_for_this_neuron = color_map[dominant_class_name]
        ax2.scatter(
            points_norm[mask, 0],
            points_norm[mask, 1],
            c=color_for_this_neuron,
            s=50,
            alpha=0.7,
            label=f'{dominant_class_name} (нейрон {neuron_id})'
        )
        if not any(dominant_class_name in elem.get_label() for elem in legend_elements):
             from matplotlib.lines import Line2D
             legend_elements.append(Line2D([0], [0], marker='o', color='w', label=dominant_class_name, markerfacecolor=color_for_this_neuron, markersize=6))
    ax2.scatter(
        final_weights[:, 0],
        final_weights[:, 1],
        c='red',
        marker='x',
        s=100,
        label='Обученные веса'
    )
    ax2.set_title('Активация нейронов Кохонена')
    ax2.set_xlabel(feature_names[0])
    ax2.set_ylabel(feature_names[1])
    ax2.legend(handles=legend_elements + [ax2.collections[-1]], loc='upper left')

    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == '__main__':
    main()