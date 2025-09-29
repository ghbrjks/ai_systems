
PROPS = ['color', 'nationality', 'drink', 'cigarette', 'pet']

DOMAINS = {
    'color':      ['red', 'green', 'white', 'yellow', 'blue'],
    'nationality':['norwegian', 'english', 'dane', 'german', 'swede'],
    'drink':      ['tea', 'coffee', 'milk', 'water', 'beer'],
    'cigarette':  ['marlboro', 'dunhill', 'rothmans', 'pall_mall', 'winfield'],
    'pet':        ['cats', 'birds', 'dogs', 'horses', 'fish']
}

houses = [ {p: None for p in PROPS} for _ in range(5) ]

solution = None

def find_pos(houses, key, value):
    # поиск номера дома по значению поля
    for i, h in enumerate(houses):
        if h[key] == value:
            return i
    return None

def neighbors(idx):
    # для поиска соседей
    res = []
    if idx - 1 >= 0: res.append(idx - 1)
    if idx + 1 <= 4: res.append(idx + 1)
    return res

def same_house_constraint(houses, keyA, valA, keyB, valB):
    # для проверки значений полей в одном доме
    posA = find_pos(houses, keyA, valA)
    posB = find_pos(houses, keyB, valB)
    if posA is not None and posB is not None:
        if posA != posB:
            return False
    if posA is not None:
        if houses[posA][keyB] is not None and houses[posA][keyB] != valB:
            return False
    if posB is not None:
        if houses[posB][keyA] is not None and houses[posB][keyA] != valA:
            return False
    return True

def neighbor_constraint(houses, keyA, valA, keyB, valB):
    # для проверки на возможность домов быть соседними
    posA = find_pos(houses, keyA, valA)
    posB = find_pos(houses, keyB, valB)

    # если оба дома известны они должны быть соседями
    if posA is not None and posB is not None:
        if abs(posA - posB) == 1:
            return True

    # если A известен, проверяем, что его сосед может быть B
    if posA is not None and posB is None:
        possible = False
        for n in neighbors(posA):
            v = houses[n][keyB]
            if v is None or v == valB:
                possible = True
                break
        if not possible:
            return False

    # если B известен
    if posB is not None and posA is None:
        possible = False
        for n in neighbors(posB):
            v = houses[n][keyA]
            if v is None or v == valA:
                possible = True
                break
        if not possible:
            return False

    return True

def left_of_constraint(houses, left_color, right_color):
    # проверка позиции домов по цветам
    posL = find_pos(houses, 'color', left_color)
    posR = find_pos(houses, 'color', right_color)

    # проверка крайних позиций домов
    if posL is not None and posL == 4:
        return False
    if posR is not None and posR == 0:
        return False

    # проверка на соседство
    if posL is not None and posR is not None:
        return posL + 1 == posR

    # проверки на соответствие цветов соседних домов
    if posL is not None and posR is None:
        right_idx = posL + 1
        if houses[right_idx]['color'] is not None and houses[right_idx]['color'] != right_color:
            return False

    if posR is not None and posL is None:
        left_idx = posR - 1
        if houses[left_idx]['color'] is not None and houses[left_idx]['color'] != left_color:
            return False

    return True

def uniqueness_check(houses):
    # значения одного свойства не должны повторяться
    for key in PROPS:
        vals = [h[key] for h in houses if h[key] is not None]
        if len(vals) != len(set(vals)):
            return False
    return True

def is_valid(houses):
    if not uniqueness_check(houses):
        return False

    # 1. Норвежец живёт в первом доме.
    if houses[0]['nationality'] is not None and houses[0]['nationality'] != 'norwegian':
        return False
    pos_nor = find_pos(houses, 'nationality', 'norwegian')
    if pos_nor is not None and pos_nor != 0:
        return False

    # 2. Англичанин живёт в красном доме.
    if not same_house_constraint(houses, 'nationality', 'english', 'color', 'red'):
        return False

    # 3. Зелёный дом находится слева от белого, рядом с ним.
    if not left_of_constraint(houses, 'green', 'white'):
        return False

    # 4. Датчанин пьёт чай.
    if not same_house_constraint(houses, 'nationality', 'dane', 'drink', 'tea'):
        return False

    # 5. Тот, кто курит Marlboro, живёт рядом с тем, кто выращивает кошек.
    if not neighbor_constraint(houses, 'cigarette', 'marlboro', 'pet', 'cats'):
        return False

    # 6. Тот, кто живёт в жёлтом доме, курит Dunhill.
    if not same_house_constraint(houses, 'color', 'yellow', 'cigarette', 'dunhill'):
        return False

    # 7. Немец курит Rothmans.
    if not same_house_constraint(houses, 'nationality', 'german', 'cigarette', 'rothmans'):
        return False

    # 8. Тот, кто живёт в центре, пьёт молоко.
    if houses[2]['drink'] is not None and houses[2]['drink'] != 'milk':
        return False
    pos_milk = find_pos(houses, 'drink', 'milk')
    if pos_milk is not None and pos_milk != 2:
        return False

    # 9. Сосед того, кто курит Marlboro, пьёт воду.
    if not neighbor_constraint(houses, 'cigarette', 'marlboro', 'drink', 'water'):
        return False

    # 10. Тот, кто курит Pall Mall, выращивает птиц.
    if not same_house_constraint(houses, 'cigarette', 'pall_mall', 'pet', 'birds'):
        return False

    # 11. Швед выращивает собак.
    if not same_house_constraint(houses, 'nationality', 'swede', 'pet', 'dogs'):
        return False

    # 12. Норвежец живёт рядом с синим домом.
    if not neighbor_constraint(houses, 'nationality', 'norwegian', 'color', 'blue'):
        return False

    # 13. Тот, кто выращивает лошадей, живёт в синем доме.
    # (двунаправленное: blue <-> horses)
    if not same_house_constraint(houses, 'pet', 'horses', 'color', 'blue'):
        return False

    # 14. Тот, кто курит Winfield, пьет пиво.
    if not same_house_constraint(houses, 'cigarette', 'winfield', 'drink', 'beer'):
        return False

    # 15. В зелёном доме пьют кофе.
    if not same_house_constraint(houses, 'color', 'green', 'drink', 'coffee'):
        return False

    return True

def backtrack(h_idx, p_idx):
    global solution
    if h_idx == 5:
        solution = ([dict(h) for h in houses])
        return True 

    prop = PROPS[p_idx]
    for val in DOMAINS[prop]:
        # пропуск уже использованных значений
        if any(h[prop] == val for h in houses):
            continue

        # присваивание значения
        houses[h_idx][prop] = val

        # проверка присвоенного значения
        if is_valid(houses):
            # сначала заполняются свойства одного дома, затем переход к следующему дому
            if p_idx < len(PROPS) - 1:
                backtrack(h_idx, p_idx + 1)
            else:
                backtrack(h_idx + 1, 0)

        # откат
        houses[h_idx][prop] = None

    return False

def query():
    print("\nДоступные свойства:", PROPS)
    while True:
        known_key = input("Введите известное свойство: ").strip().lower()
        if known_key not in PROPS:
            print("Некорректное свойство. Попробуйте снова.")
            continue
        known_value = input(f"Введите значение для {known_key}: ").strip().lower()
        target_key = input("Какое свойство хотите узнать? ").strip().lower()
        if target_key not in PROPS:
            print("Некорректное свойство. Попробуйте снова.")
            continue

        # поиск значения
        found = None
        for h in solution:
            if h[known_key].lower() == known_value:
                found = h[target_key]
                break
        if found:
            print(f"{target_key.capitalize()} для {known_key}={known_value} -> {found}")
        else:
            print("Не найдено дома с таким значением.")

def print_solution(sol):
    print("{:>2} {:>8} {:>12} {:>8} {:>12} {:>8}\n".format("№","color","nationality","drink","cigarette","pet"))
    for i,h in enumerate(sol):
        print("{:2d} {:>8} {:>12} {:>8} {:>12} {:>8}".format(
            i+1, h['color'], h['nationality'], h['drink'], h['cigarette'], h['pet']
        ))

if __name__ == "__main__":
    backtrack(0, 0)
    if solution is None:
        print("Решений не найдено.")
    else:
        print_solution(solution)
        query()
