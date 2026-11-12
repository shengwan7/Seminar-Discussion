import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).with_name(".mplconfig")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


# =========================
# 能量模型與模擬參數
# =========================
E_ELEC = 50e-9       # 50 nJ/bit
EPS_AMP = 100e-12    # 100 pJ/bit/m^2
E_FUSION = 5e-9      # 5 nJ/bit/message
PACKET_SIZE = 2000   # bits
INIT_ENERGY = 0.5    # J
NUM_NODES = 100
FIELD_SIZE = 50      # 50m x 50m
BS_POS = np.array((25.0, 150.0))  # 基地台位置
MAX_ROUNDS = 100000

DEATH_RATIOS = (0.01, 0.20, 0.50, 1.00)
DEATH_LABELS = ("1%", "20%", "50%", "100%")


@dataclass
class SimulationResult:
    """儲存單一協議在各死亡比例下的輪數。"""

    name: str
    rounds: dict[str, int]


def tx_energy(distance: float) -> float:
    """計算傳輸一個封包到指定距離所需能量。"""
    return E_ELEC * PACKET_SIZE + EPS_AMP * PACKET_SIZE * distance**2


def rx_energy() -> float:
    """計算接收一個封包所需能量。"""
    return E_ELEC * PACKET_SIZE


def fusion_energy(message_count: int = 1) -> float:
    """計算融合指定數量訊息所需能量。"""
    return E_FUSION * PACKET_SIZE * message_count


def distance(a: np.ndarray, b: np.ndarray) -> float:
    """計算兩點間歐氏距離。"""
    return float(np.linalg.norm(a - b))


def record_deaths(energies: np.ndarray, round_no: int, records: dict[str, int | None]) -> None:
    """若死亡節點數達門檻，就記錄第一次達成的輪數。"""
    dead_count = int(np.count_nonzero(energies <= 0))
    for ratio, label in zip(DEATH_RATIOS, DEATH_LABELS):
        threshold = math.ceil(NUM_NODES * ratio)
        if records[label] is None and dead_count >= threshold:
            records[label] = round_no


def finalize_records(records: dict[str, int | None]) -> dict[str, int]:
    """若在最大輪數內沒有達到門檻，以 MAX_ROUNDS 表示上限結果。"""
    return {label: (MAX_ROUNDS if value is None else value) for label, value in records.items()}


def initial_records() -> dict[str, int | None]:
    """建立死亡比例記錄表。"""
    return {label: None for label in DEATH_LABELS}


def simulate_direct(positions: np.ndarray) -> SimulationResult:
    """Direct Transmission：每個存活節點每輪直接傳給基地台。"""
    energies = np.full(NUM_NODES, INIT_ENERGY, dtype=float)
    records = initial_records()
    bs_distances = np.linalg.norm(positions - BS_POS, axis=1)

    for round_no in range(1, MAX_ROUNDS + 1):
        alive = np.where(energies > 0)[0]
        if alive.size == 0:
            record_deaths(energies, round_no - 1, records)
            break

        # 每個存活節點直接傳送一個封包給基地台。
        for node in alive:
            energies[node] -= tx_energy(float(bs_distances[node]))

        record_deaths(energies, round_no, records)
        if records["100%"] is not None:
            break

    return SimulationResult("Direct", finalize_records(records))


def choose_cluster_heads(alive: np.ndarray, used_heads: set[int]) -> tuple[np.ndarray, set[int]]:
    """LEACH：從尚未當過簇頭的存活節點中選出約 5% 作為簇頭。"""
    cluster_head_count = max(1, math.ceil(alive.size * 0.05))
    eligible = np.array([node for node in alive if node not in used_heads], dtype=int)

    # 若一個輪替週期用完，重新開放所有存活節點成為簇頭。
    if eligible.size < cluster_head_count:
        used_heads.clear()
        eligible = alive.copy()

    selected_count = min(cluster_head_count, eligible.size)
    cluster_heads = np.random.choice(eligible, size=selected_count, replace=False)
    used_heads.update(int(node) for node in cluster_heads)
    return cluster_heads, used_heads


def simulate_leach(positions: np.ndarray) -> SimulationResult:
    """LEACH：隨機輪替簇頭，非簇頭加入最近簇頭。"""
    energies = np.full(NUM_NODES, INIT_ENERGY, dtype=float)
    records = initial_records()
    used_heads: set[int] = set()

    for round_no in range(1, MAX_ROUNDS + 1):
        alive = np.where(energies > 0)[0]
        if alive.size == 0:
            record_deaths(energies, round_no - 1, records)
            break

        cluster_heads, used_heads = choose_cluster_heads(alive, used_heads)
        cluster_head_set = set(int(node) for node in cluster_heads)
        members_by_head = {int(head): [] for head in cluster_heads}

        # 非簇頭節點加入最近的簇頭，並傳送資料給該簇頭。
        for node in alive:
            if int(node) in cluster_head_set:
                continue
            nearest_head = min(cluster_heads, key=lambda head: distance(positions[node], positions[head]))
            members_by_head[int(nearest_head)].append(int(node))
            energies[node] -= tx_energy(distance(positions[node], positions[nearest_head]))

        # 簇頭接收簇內資料、融合資料後，傳送一個封包給基地台。
        for head in cluster_heads:
            members = members_by_head[int(head)]
            energies[head] -= rx_energy() * len(members)
            energies[head] -= fusion_energy(len(members) + 1)
            energies[head] -= tx_energy(distance(positions[head], BS_POS))

        record_deaths(energies, round_no, records)
        if records["100%"] is not None:
            break

    return SimulationResult("LEACH", finalize_records(records))


def build_pegasis_chain(positions: np.ndarray, alive: np.ndarray) -> list[int]:
    """PEGASIS：從離基地台最遠的節點開始，以貪心法建立鏈。"""
    if alive.size == 0:
        return []

    alive_set = set(int(node) for node in alive)
    farthest = max(alive_set, key=lambda node: distance(positions[node], BS_POS))
    chain = [farthest]
    alive_set.remove(farthest)

    while alive_set:
        current = chain[-1]
        nearest = min(alive_set, key=lambda node: distance(positions[current], positions[node]))
        chain.append(nearest)
        alive_set.remove(nearest)

    return chain


def spend_pegasis_side(
    chain: list[int],
    positions: np.ndarray,
    energies: np.ndarray,
    start_index: int,
    stop_index: int,
    step: int,
) -> int:
    """讓鏈頭一側的資料逐段傳向鏈頭，回傳鏈頭收到的訊息數。"""
    received_by_head = 0

    for index in range(start_index, stop_index, step):
        sender = chain[index]
        receiver = chain[index + step]
        hop_distance = distance(positions[sender], positions[receiver])

        energies[sender] -= tx_energy(hop_distance)
        energies[receiver] -= rx_energy()

        # 中繼節點融合收到的資料，鏈頭的融合統一在主流程計算。
        if receiver != chain[stop_index]:
            energies[receiver] -= fusion_energy()
        else:
            received_by_head += 1

    return received_by_head


def simulate_pegasis(positions: np.ndarray) -> SimulationResult:
    """PEGASIS：鏈式傳輸，鏈頭輪替並負責送往基地台。"""
    energies = np.full(NUM_NODES, INIT_ENERGY, dtype=float)
    records = initial_records()
    chain: list[int] = []
    previous_alive: tuple[int, ...] = ()

    for round_no in range(1, MAX_ROUNDS + 1):
        alive = np.where(energies > 0)[0]
        alive_key = tuple(int(node) for node in alive)
        if alive.size == 0:
            record_deaths(energies, round_no - 1, records)
            break

        # 節點死亡後重建鏈；若存活集合不變，沿用原鏈節省運算。
        if alive_key != previous_alive:
            chain = build_pegasis_chain(positions, alive)
            previous_alive = alive_key

        head_position = round_no % len(chain)
        head = chain[head_position]

        # 鏈頭左右兩側分別把資料往鏈頭方向傳遞。
        messages_to_head = 0
        if head_position > 0:
            messages_to_head += spend_pegasis_side(chain, positions, energies, 0, head_position, 1)
        if head_position < len(chain) - 1:
            messages_to_head += spend_pegasis_side(
                chain,
                positions,
                energies,
                len(chain) - 1,
                head_position,
                -1,
            )

        energies[head] -= fusion_energy(messages_to_head + 1)
        energies[head] -= tx_energy(distance(positions[head], BS_POS))

        record_deaths(energies, round_no, records)
        if records["100%"] is not None:
            break

    return SimulationResult("PEGASIS", finalize_records(records))


def print_results(results: list[SimulationResult]) -> None:
    """依指定格式印出死亡輪數對照表。"""
    print("=== 節點死亡輪數 ===")
    print(f"{'協議':<10}{'1%':>8}{'20%':>8}{'50%':>8}{'100%':>8}")
    for result in results:
        print(
            f"{result.name:<10}"
            f"{result.rounds['1%']:>8}"
            f"{result.rounds['20%']:>8}"
            f"{result.rounds['50%']:>8}"
            f"{result.rounds['100%']:>8}"
        )


def plot_results(results: list[SimulationResult]) -> None:
    """繪製三種協議在各死亡比例下的輪數比較長條圖。"""
    setup_chinese_font()

    x = np.arange(len(DEATH_LABELS))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for index, result in enumerate(results):
        offsets = x + (index - 1) * width
        values = [result.rounds[label] for label in DEATH_LABELS]
        ax.bar(offsets, values, width, label=result.name)

    ax.set_xlabel("死亡比例")
    ax.set_ylabel("輪數")
    ax.set_title("WSN 路由協議節點死亡輪數比較")
    ax.set_xticks(x)
    ax.set_xticklabels(DEATH_LABELS)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig("comparison.png", dpi=300)
    plt.close(fig)


def setup_chinese_font() -> None:
    """設定 matplotlib 可用的中文字型，避免圖表中文缺字。"""
    candidates = [
        "Microsoft JhengHei",
        "Noto Sans TC",
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
    ]
    installed_fonts = {font.name for font in fm.fontManager.ttflist}

    for font_name in candidates:
        if font_name in installed_fonts:
            plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return


def main() -> None:
    """主程式：產生固定節點位置，執行三種協議並輸出結果。"""
    np.random.seed(42)
    positions = np.random.uniform(0, FIELD_SIZE, size=(NUM_NODES, 2))

    results = [
        simulate_direct(positions),
        simulate_leach(positions),
        simulate_pegasis(positions),
    ]

    print_results(results)
    plot_results(results)
    print("\n圖表已儲存為 comparison.png")


if __name__ == "__main__":
    main()
