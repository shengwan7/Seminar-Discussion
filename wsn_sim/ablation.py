import os
import sys
from dataclasses import dataclass
import math
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).with_name(".mplconfig")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

import matplotlib.pyplot as plt
import numpy as np

from simulate import (
    BS_POS,
    FIELD_SIZE,
    INIT_ENERGY,
    MAX_ROUNDS,
    NUM_NODES,
    build_pegasis_chain,
    choose_cluster_heads,
    distance,
    fusion_energy,
    rx_energy,
    setup_chinese_font,
    tx_energy,
)


# 消融實驗只比較三個死亡比例。
DEATH_RATIOS = (0.01, 0.50, 1.00)
DEATH_LABELS = ("1%", "50%", "100%")
OUTPUT_DIR = Path(__file__).resolve().parent


@dataclass
class AblationResult:
    """儲存消融實驗中單一協議的結果。"""

    name: str
    rounds: dict[str, int]
    energy_std: float


def initial_records() -> dict[str, int | None]:
    """建立消融實驗需要的死亡比例記錄表。"""
    return {label: None for label in DEATH_LABELS}


def finalize_records(records: dict[str, int | None]) -> dict[str, int]:
    """若最大輪數內未達門檻，以 MAX_ROUNDS 作為上限結果。"""
    return {label: (MAX_ROUNDS if value is None else value) for label, value in records.items()}


def record_ablation_deaths(energies: np.ndarray, round_no: int, records: dict[str, int | None]) -> None:
    """記錄 1%、50%、100% 節點第一次死亡達標的輪數。"""
    dead_count = int(np.count_nonzero(energies <= 0))
    for ratio, label in zip(DEATH_RATIOS, DEATH_LABELS):
        threshold = math.ceil(NUM_NODES * ratio)
        if records[label] is None and dead_count >= threshold:
            records[label] = round_no


def final_energy_std(energies: np.ndarray) -> float:
    """計算模擬結束時所有節點能量消耗量的標準差。"""
    consumed_energy = INIT_ENERGY - energies
    return float(np.std(consumed_energy))


def simulate_leach_ablation(positions: np.ndarray) -> AblationResult:
    """LEACH 對照組：沿用現有分簇與簇頭輪換邏輯。"""
    energies = np.full(NUM_NODES, INIT_ENERGY, dtype=float)
    records = initial_records()
    used_heads: set[int] = set()

    for round_no in range(1, MAX_ROUNDS + 1):
        alive = np.where(energies > 0)[0]
        if alive.size == 0:
            record_ablation_deaths(energies, round_no - 1, records)
            break

        cluster_heads, used_heads = choose_cluster_heads(alive, used_heads)
        cluster_head_set = set(int(node) for node in cluster_heads)
        members_by_head = {int(head): [] for head in cluster_heads}

        # 非簇頭節點選擇最近簇頭，並把資料傳給簇頭。
        for node in alive:
            if int(node) in cluster_head_set:
                continue
            nearest_head = min(cluster_heads, key=lambda head: distance(positions[node], positions[head]))
            members_by_head[int(nearest_head)].append(int(node))
            energies[node] -= tx_energy(distance(positions[node], positions[nearest_head]))

        # 簇頭負責接收、融合，並將融合後資料傳給基地台。
        for head in cluster_heads:
            members = members_by_head[int(head)]
            energies[head] -= rx_energy() * len(members)
            energies[head] -= fusion_energy(len(members) + 1)
            energies[head] -= tx_energy(distance(positions[head], BS_POS))

        record_ablation_deaths(energies, round_no, records)
        if records["100%"] is not None:
            break

    return AblationResult("LEACH", finalize_records(records), final_energy_std(energies))


def spend_chain_side(
    chain: list[int],
    positions: np.ndarray,
    energies: np.ndarray,
    start_index: int,
    stop_index: int,
    step: int,
) -> int:
    """讓鏈頭一側的節點沿鏈傳輸資料，回傳鏈頭收到的訊息數。"""
    received_by_head = 0

    for index in range(start_index, stop_index, step):
        sender = chain[index]
        receiver = chain[index + step]
        hop_distance = distance(positions[sender], positions[receiver])

        energies[sender] -= tx_energy(hop_distance)
        energies[receiver] -= rx_energy()

        # 中繼節點融合收到的資料；鏈頭融合在主流程統一計算。
        if receiver != chain[stop_index]:
            energies[receiver] -= fusion_energy()
        else:
            received_by_head += 1

    return received_by_head


def choose_proposed_head(chain: list[int], positions: np.ndarray, energies: np.ndarray) -> tuple[int, int]:
    """改進版 PEGASIS：選擇剩餘能量 / 到基地台距離 最大的存活節點當鏈頭。"""
    scores = []
    for index, node in enumerate(chain):
        bs_distance = max(distance(positions[node], BS_POS), 1e-12)
        scores.append((energies[node] / bs_distance, index, node))

    _, head_position, head = max(scores, key=lambda item: item[0])
    return head_position, head


def simulate_pegasis_ablation(positions: np.ndarray, proposed: bool = False) -> AblationResult:
    """模擬 Baseline PEGASIS 或 Proposed PEGASIS。"""
    energies = np.full(NUM_NODES, INIT_ENERGY, dtype=float)
    records = initial_records()
    chain: list[int] = []
    previous_alive: tuple[int, ...] = ()

    for round_no in range(1, MAX_ROUNDS + 1):
        alive = np.where(energies > 0)[0]
        alive_key = tuple(int(node) for node in alive)
        if alive.size == 0:
            record_ablation_deaths(energies, round_no - 1, records)
            break

        # 節點死亡後重建鏈；存活集合未變時沿用原鏈。
        if alive_key != previous_alive:
            chain = build_pegasis_chain(positions, alive)
            previous_alive = alive_key

        if proposed:
            head_position, head = choose_proposed_head(chain, positions, energies)
        else:
            # Baseline PEGASIS：沿用原始 rounds % N 的輪換精神。
            head_position = round_no % len(chain)
            head = chain[head_position]

        # 鏈頭左右兩側分別把資料往鏈頭傳遞。
        messages_to_head = 0
        if head_position > 0:
            messages_to_head += spend_chain_side(chain, positions, energies, 0, head_position, 1)
        if head_position < len(chain) - 1:
            messages_to_head += spend_chain_side(
                chain,
                positions,
                energies,
                len(chain) - 1,
                head_position,
                -1,
            )

        energies[head] -= fusion_energy(messages_to_head + 1)
        energies[head] -= tx_energy(distance(positions[head], BS_POS))

        record_ablation_deaths(energies, round_no, records)
        if records["100%"] is not None:
            break

    name = "Proposed" if proposed else "PEGASIS"
    return AblationResult(name, finalize_records(records), final_energy_std(energies))


def print_results(results: list[AblationResult]) -> None:
    """依指定格式印出消融實驗矩陣表。"""
    print("=== 消融實驗結果 ===")
    print(f"{'協議':<12}{'1%':>8}{'50%':>8}{'100%':>8}{'能量標準差':>14}")
    for result in results:
        print(
            f"{result.name:<12}"
            f"{result.rounds['1%']:>8}"
            f"{result.rounds['50%']:>8}"
            f"{result.rounds['100%']:>8}"
            f"{result.energy_std:>14.6f}"
        )


def plot_results(results: list[AblationResult]) -> None:
    """繪製三種協議與三個死亡比例的長條圖。"""
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
    ax.set_title("PEGASIS 鏈頭選擇消融實驗")
    ax.set_xticks(x)
    ax.set_xticklabels(DEATH_LABELS)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "ablation.png", dpi=300)
    plt.close(fig)


def write_markdown_report(results: list[AblationResult]) -> None:
    """將消融實驗結果輸出為 Markdown 報告。"""
    lines = [
        "# PEGASIS 鏈頭選擇消融實驗結果",
        "",
        "本實驗比較 LEACH、Baseline PEGASIS 與 Proposed PEGASIS。Proposed PEGASIS 將鏈頭選擇由固定輪換改為每輪選擇「剩餘能量 / 到基地台距離」最大的存活節點，其餘 PEGASIS 傳輸與鏈重建邏輯保持相同。",
        "",
        "## 結果矩陣",
        "",
        "| 協議 | 1% | 50% | 100% | 能量標準差 |",
        "|---|---:|---:|---:|---:|",
    ]

    for result in results:
        lines.append(
            f"| {result.name} | {result.rounds['1%']} | {result.rounds['50%']} | "
            f"{result.rounds['100%']} | {result.energy_std:.6f} |"
        )

    lines.extend(
        [
            "",
            "能量標準差為模擬結束時所有節點能量消耗量的標準差；由於每輪扣能為離散事件，節點死亡當輪可能出現小幅負值。",
            "",
            "## 圖表",
            "",
            "![ablation](ablation.png)",
            "",
        ]
    )

    (OUTPUT_DIR / "ablation_results.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """主程式：固定隨機種子，執行三種協議的消融實驗。"""
    np.random.seed(42)
    positions = np.random.uniform(0, FIELD_SIZE, size=(NUM_NODES, 2))

    results = [
        simulate_leach_ablation(positions),
        simulate_pegasis_ablation(positions, proposed=False),
        simulate_pegasis_ablation(positions, proposed=True),
    ]

    print_results(results)
    plot_results(results)
    write_markdown_report(results)
    print("\n圖表已儲存為 ablation.png")
    print("結果已寫入 ablation_results.md")


if __name__ == "__main__":
    main()
