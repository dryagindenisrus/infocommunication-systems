import random
from collections import deque


def generate_graph(N, P):
    """Генерирует случайный граф по вероятностям P (adjacency list)"""
    G = [[] for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            if random.random() < P[i][j]:
                G[i].append(j)
                G[j].append(i)
    return G


def has_path(G, start, goal, N):
    """Проверка существования пути"""
    if start == goal:
        return True
    visited = [False] * N
    queue = deque([start])
    visited[start] = True
    while queue:
        u = queue.popleft()
        for v in G[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
                if v == goal:
                    return True
    return False


def is_connected(G, N):
    """Проверка, является ли граф связным (BFS от вершины 0)"""
    if N == 0:
        return True
    visited = [False] * N
    queue = deque([0])
    visited[0] = True
    count = 1
    while queue:
        u = queue.popleft()
        for v in G[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
                count += 1
    return count == N


def check_ab_connected(G, N, A, B):
    """Проверка пути A → B (для ЛР1)"""
    return has_path(G, A, B, N)


def check_fully_connected(G, N, A=None, B=None):
    """Проверка связности всего графа (для ЛР2)"""
    return is_connected(G, N)


def simulate_probability(N, P, num_sim, check_func, A=None, B=None):
    """Моделирование (Монте-Карло)"""
    count = 0
    for _ in range(num_sim):
        G = generate_graph(N, P)
        if check_func(G, N, A, B):
            count += 1
    return count / num_sim


def exact_probability(N, P, check_func, A=None, B=None):
    """Полный перебор всех 2^M возможных подграфов"""
    possible_edges = [(i, j) for i in range(N) for j in range(i + 1, N)]
    M = len(possible_edges)
    total = 0.0
    for mask in range(1 << M):  # 0 .. 2^M - 1
        prob = 1.0
        G = [[] for _ in range(N)]
        for k, (i, j) in enumerate(possible_edges):
            p_e = P[i][j]
            include = bool(mask & (1 << k))
            prob *= p_e if include else (1 - p_e)
            if include:
                G[i].append(j)
                G[j].append(i)
        # Добавляем вероятность, если подграф удовлетворяет условию
        if check_func(G, N, A, B):
            total += prob
    return total


# ====================== ОСНОВНАЯ ПРОГРАММА ======================
if __name__ == "__main__":
    print("=== Лабораторные работы по случайным графам ===\n")

    N = int(input("Введите количество вершин N: "))
    P = [[0.0 for _ in range(N)] for _ in range(N)]

    print("Введите вероятности существования рёбер (для каждой пары i < j):")
    for i in range(N):
        for j in range(i + 1, N):
            p = float(input(f"  p[{i}][{j}] = "))
            P[i][j] = p
            P[j][i] = p  # симметричная матрица

    A = int(input(f"\nДля ЛР1: введите номер узла A (0..{N - 1}): "))
    B = int(input(f"Для ЛР1: введите номер узла B (0..{N - 1}): "))

    num_sim = int(input("\nКоличество симуляций для моделирования: ") or 100000)

    print("\n" + "=" * 60)
    print("ЛР 1: Вероятность существования пути из A в B")
    print("=" * 60)

    prob_sim_ab = simulate_probability(N, P, num_sim, check_ab_connected, A, B)
    print(f"1) Моделирование (Монте-Карло):          {prob_sim_ab:.8f}")

    prob_exact_ab = exact_probability(N, P, check_ab_connected, A, B)
    print(f"2) Полный перебор всех подграфов:         {prob_exact_ab:.8f}")

    print("\n" + "=" * 60)
    print("ЛР 2: Вероятность связного графа")
    print("=" * 60)

    prob_sim_conn = simulate_probability(N, P, num_sim, check_fully_connected)
    print(f"1) Моделирование (Монте-Карло):          {prob_sim_conn:.8f}")

    prob_exact_conn = exact_probability(N, P, check_fully_connected)
    print(f"2) Полный перебор всех подграфов:         {prob_exact_conn:.8f}")