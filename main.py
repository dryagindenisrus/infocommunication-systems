import os
import random
from collections import deque
import subprocess
import matplotlib.pyplot as plt

NUM_SIMULATIONS = [
    5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 45, 50, 55, 60,
    70, 80, 90, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400, 450, 500,
    600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 3000, 4000, 5000, 10000
]
A = 0
B = 3


def parse_dot_file(filepath):
    """Parse .dot file to extract graph structure and edge probabilities"""
    edges = []
    N = 0

    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        line = line.rstrip(';').strip()

        if '--' in line:
            parts = line.split('--')
            left = parts[0].strip()
            right = parts[1].split('[')[0].strip()
            prob = 0.5
            if 'label' in line:
                try:
                    label_part = line.split('label=')[1].split(']')[0]
                    label_part = label_part.strip()
                    if label_part.startswith('"') and label_part.endswith('"'):
                        label_part = label_part[1:-1]
                    prob = float(label_part)
                except:
                    pass
            a, b = int(left), int(right)
            edges.append((a, b, prob))
            N = max(N, a + 1, b + 1)

        elif '->' in line:
            parts = line.split('->')
            left = parts[0].strip()
            right = parts[1].split('[')[0].strip()
            prob = 0.5
            if 'label' in line:
                try:
                    label_part = line.split('label=')[1].split(']')[0]
                    label_part = label_part.strip()
                    if label_part.startswith('"') and label_part.endswith('"'):
                        label_part = label_part[1:-1]
                    prob = float(label_part)
                except:
                    pass
            a, b = int(left), int(right)
            edges.append((a, b, prob))
            N = max(N, a + 1, b + 1)

    return N, edges


def build_P_matrix(N, edges):
    """Build probability matrix from edges"""
    P = [[0.0 for _ in range(N)] for _ in range(N)]
    for a, b, prob in edges:
        P[a][b] = prob
        P[b][a] = prob
    return P


def generate_graph(N, P):
    """Generate random graph by probabilities P"""
    G = [[] for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            if random.random() < P[i][j]:
                G[i].append(j)
                G[j].append(i)
    return G


def has_path(G, start, goal, N):
    """Check if path exists"""
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
    """Check if graph is connected"""
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
    """Check path A -> B"""
    return has_path(G, A, B, N)


def check_fully_connected(G, N, A=None, B=None):
    """Check full connectivity"""
    return is_connected(G, N)


def simulate_probability(N, P, num_sim, check_func, A=None, B=None):
    """Monte Carlo simulation"""
    count = 0
    for _ in range(num_sim):
        G = generate_graph(N, P)
        if check_func(G, N, A, B):
            count += 1
    return count / num_sim


def exact_probability(N, P, check_func, A=None, B=None):
    """Full enumeration of all 2^M subgraphs"""
    possible_edges = [(i, j) for i in range(N) for j in range(i + 1, N)]
    M = len(possible_edges)
    total = 0.0
    for mask in range(1 << M):
        prob = 1.0
        G = [[] for _ in range(N)]
        for k, (i, j) in enumerate(possible_edges):
            p_e = P[i][j]
            include = bool(mask & (1 << k))
            prob *= p_e if include else (1 - p_e)
            if include:
                G[i].append(j)
                G[j].append(i)
        if check_func(G, N, A, B):
            total += prob
    return total


def ensure_dir(path):
    """Create directory if not exists"""
    if not os.path.exists(path):
        os.makedirs(path)


def render_graph_dot(dot_path, output_path):
    """Render .dot file to image using graphviz"""
    try:
        subprocess.run(['dot', '-Tpng', dot_path, '-o', output_path], check=True, capture_output=True)
    except Exception:
        pass


def plot_simulation_comparison(sim_counts, lr1_results, lr2_results, exact1, exact2, output_path):
    """Plot comparison chart for Monte Carlo vs exact probability"""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(sim_counts, lr1_results, 'b-o', label='LR1: Path A->B (Monte Carlo)', linewidth=2)
    ax.axhline(y=exact1, color='b', linestyle='--', alpha=0.7, label=f'LR1: Exact ({exact1:.4f})')

    ax.plot(sim_counts, lr2_results, 'r-s', label='LR2: Connectivity (Monte Carlo)', linewidth=2)
    ax.axhline(y=exact2, color='r', linestyle='--', alpha=0.7, label=f'LR2: Exact ({exact2:.4f})')

    ax.set_xlabel('Number of Simulations')
    ax.set_ylabel('Probability')
    ax.set_xscale('log')
    ax.set_ylim(0, 1)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def process_graph(dot_path):
    """Process single graph file"""
    graph_name = os.path.splitext(os.path.basename(dot_path))[0]
    results_dir = f'results/{graph_name}'
    ensure_dir(results_dir)

    N, edges = parse_dot_file(dot_path)
    P = build_P_matrix(N, edges)

    render_graph_dot(dot_path, f'{results_dir}/original_graph.png')

    exact1 = exact_probability(N, P, check_ab_connected, A, B)
    exact2 = exact_probability(N, P, check_fully_connected)

    lr1_sim_results = []
    lr2_sim_results = []

    for num_sim in NUM_SIMULATIONS:
        prob_sim_ab = simulate_probability(N, P, num_sim, check_ab_connected, A, B)
        prob_sim_conn = simulate_probability(N, P, num_sim, check_fully_connected)
        lr1_sim_results.append(prob_sim_ab)
        lr2_sim_results.append(prob_sim_conn)

    plot_simulation_comparison(
        NUM_SIMULATIONS, lr1_sim_results, lr2_sim_results,
        exact1, exact2,
        f'{results_dir}/connectivity_comparison_chart.png'
    )

    with open(f'{results_dir}/result.txt', 'w') as f:
        f.write(f"Graph: {graph_name}\n")
        f.write(f"N={N}, A={A}, B={B}\n\n")
        f.write("LR 1: Probability of path existence from A to B\n")
        f.write(f"1) Monte-Carlo simulation:          {lr1_sim_results[-1]:.8f} (N={NUM_SIMULATIONS[-1]})\n")
        f.write(f"2) Full enumeration of subgraphs:   {exact1:.8f}\n\n")
        f.write("LR 2: Probability of connected graph\n")
        f.write(f"1) Monte-Carlo simulation:          {lr2_sim_results[-1]:.8f} (N={NUM_SIMULATIONS[-1]})\n")
        f.write(f"2) Full enumeration of subgraphs:    {exact2:.8f}\n")


def main():
    input_dir = 'input'
    dot_files = [f for f in os.listdir(input_dir) if f.endswith('.dot')]

    for dot_file in sorted(dot_files):
        process_graph(os.path.join(input_dir, dot_file))


if __name__ == "__main__":
    main()