
PROPS = ['цвет', 'национальность', 'напиток', 'сигареты', 'животное']

DOMAINS = {
    'цвет':      ['красный', 'зеленый', 'белый', 'желтый', 'синий'],
    'национальность':['норвежец', 'англичанин', 'датчанин', 'немец', 'швед'],
    'напиток':      ['чай', 'кофе', 'молоко', 'вода', 'пиво'],
    'сигареты':  ['мальборо', 'данхилл', 'ротманс', 'поллмолл', 'винфилд'],
    'животное':        ['кошки', 'птицы', 'собаки', 'лошади', 'рыбки']
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
        else:
            return False

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

def left_of_constraint(houses, left_цвет, right_цвет):
    # проверка позиции домов по цветам
    posL = find_pos(houses, 'цвет', left_цвет)
    posR = find_pos(houses, 'цвет', right_цвет)

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
        if houses[right_idx]['цвет'] is not None and houses[right_idx]['цвет'] != right_цвет:
            return False

    if posR is not None and posL is None:
        left_idx = posR - 1
        if houses[left_idx]['цвет'] is not None and houses[left_idx]['цвет'] != left_цвет:
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
    if houses[0]['национальность'] is not None and houses[0]['национальность'] != 'норвежец':
        return False
    pos_nor = find_pos(houses, 'национальность', 'норвежец')
    if pos_nor is not None and pos_nor != 0:
        return False

    # 2. Англичанин живёт в красном доме.
    if not same_house_constraint(houses, 'национальность', 'англичанин', 'цвет', 'красный'):
        return False

    # 3. Зелёный дом находится слева от белого, рядом с ним.
    if not left_of_constraint(houses, 'зеленый', 'белый'):
        return False

    # 4. Датчанин пьёт чай.
    if not same_house_constraint(houses, 'национальность', 'датчанин', 'напиток', 'чай'):
        return False

    # 5. Тот, кто курит мальборо, живёт рядом с тем, кто выращивает кошек.
    if not neighbor_constraint(houses, 'сигареты', 'мальборо', 'животное', 'кошки'):
        return False

    # 6. Тот, кто живёт в жёлтом доме, курит данхилл.
    if not same_house_constraint(houses, 'цвет', 'желтый', 'сигареты', 'данхилл'):
        return False

    # 7. Немец курит ротманс.
    if not same_house_constraint(houses, 'национальность', 'немец', 'сигареты', 'ротманс'):
        return False

    # 8. Тот, кто живёт в центре, пьёт молоко.
    if houses[2]['напиток'] is not None and houses[2]['напиток'] != 'молоко':
        return False
    pos_молоко = find_pos(houses, 'напиток', 'молоко')
    if pos_молоко is not None and pos_молоко != 2:
        return False

    # 9. Сосед того, кто курит мальборо, пьёт воду.
    if not neighbor_constraint(houses, 'сигареты', 'мальборо', 'напиток', 'вода'):
        return False

    # 10. Тот, кто курит Pall Mall, выращивает птиц.
    if not same_house_constraint(houses, 'сигареты', 'поллмолл', 'животное', 'птицы'):
        return False

    # 11. Швед выращивает собак.
    if not same_house_constraint(houses, 'национальность', 'швед', 'животное', 'собаки'):
        return False

    # 12. Норвежец живёт рядом с синим домом.
    if not neighbor_constraint(houses, 'национальность', 'норвежец', 'цвет', 'синий'):
        return False

    # 13. Тот, кто выращивает лошадей, живёт в синем доме.
    # (двунаправленное: синий <-> лошади)
    if not same_house_constraint(houses, 'животное', 'лошади', 'цвет', 'синий'):
        return False

    # 14. Тот, кто курит винфилд, пьет пиво.
    if not same_house_constraint(houses, 'сигареты', 'винфилд', 'напиток', 'пиво'):
        return False

    # 15. В зелёном доме пьют кофе.
    if not same_house_constraint(houses, 'цвет', 'зеленый', 'напиток', 'кофе'):
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

def prolog_like_query():
    print("\nДоступные свойства:", PROPS)
    while True:
        known_keys = {}
        target_keys = {}
        dict_keys = list(DOMAINS.values())
        for word in dict_keys:
            print(word)
        request = input(f"Введите запрос: ").replace(" ","").lower().split(",")
        for word_req in request:
            for i in range(5):
                if word_req == "_":
                    continue
                elif word_req == dict_keys[i]:
                    index = request.index(word_req)
                    known_keys[index] = word_req
                else:
                    index = request.index(word_req)
                    target_keys[index] = word_req
        keys_k = list(known_keys.keys())
        values_k = list(known_keys.values())
        keys_t = list(target_keys.keys())
        values_t = list(target_keys.values())
        print("Индекс известных ключей")
        for word in keys_k:
            print("!",word,"!")
        print("Значение известных ключей")
        for word in values_k:
            print("!",word,"!")
        print("Индекс искомых ключей")
        for word in keys_t:
            print(word)
        print("Значение искомых ключей")
        for word in values_t:
            print(word)



def print_solution(sol):
    print("{:>2} {:>8} {:>12} {:>8} {:>12} {:>8}\n".format("№","цвет","национальность","напиток","сигареты","животное"))
    for i,h in enumerate(sol):
        print("{:2d} {:>8} {:>12} {:>8} {:>12} {:>8}".format(
            i+1, h['цвет'], h['национальность'], h['напиток'], h['сигареты'], h['животное']
        ))

if __name__ == "__main__":
    backtrack(0, 0)
    if solution is None:
        print("Решений не найдено.")
    else:
        print_solution(solution)
        prolog_like_query()
