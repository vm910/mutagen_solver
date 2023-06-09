from colorama import Fore, Style
from collections import deque
import numpy as np


def printd(d: dict) -> None:
    for key, value in d.items():
        colored_values = [
            f"{Fore.RED}{atom}{Style.RESET_ALL}"
            if atom.startswith("-")
            else f"{Fore.GREEN}{atom}{Style.RESET_ALL}"
            for atom in value
        ]
        print(f"\t{key}: {' '.join(map(str, colored_values))}")
    print("\n")


def flatten(l: list[list]) -> list:
    return [item for sublist in l for item in sublist]


def parse_reagents(path: str) -> dict:
    with open(path, "r") as f:
        reagents = f.readlines()
        reagents = [reagent.strip() for reagent in reagents]
        reagents = [reagent.split(" ") for reagent in reagents]
        mut_dict = dict(map(lambda reagents: (reagents[0], reagents[1:]), reagents))

        EXITUS = mut_dict.pop("Exitus-1")
        return mut_dict, EXITUS


def filter_useless_reagents(reagents: dict, EXITUS: list[str]) -> dict:
    while True:
        reagents_c = reagents.copy()
        atom_pool = set(flatten(list(reagents_c.values())))

        for key, reagent in reagents_c.items():
            for atom in reagent:
                if (
                    atom[0] != "-"
                    and atom not in EXITUS
                    and "-" + atom not in atom_pool
                    and key in reagents
                ):
                    reagents.pop(key)
                    break
        if reagents == reagents_c:
            break

    return reagents


def combine_reagents(reagent1: list[str], reagent2: list[str]) -> list[str]:
    reagent1_set = set(reagent1)
    reagent2_set = set(reagent2)

    r1 = [
        atom for atom in reagent1 if atom[0] != "-" and "-" + atom not in reagent2_set
    ]
    r2 = [atom for atom in reagent2 if atom[0] != "-" and atom not in reagent1_set]

    return r1 + r2


def color_eliminated_atoms(reagent1: list[str], reagent2: list[str]):
    color_values1 = []
    color_values2 = []

    for atom in reagent1:
        if "-" + atom in reagent2:
            color_values1.append(f"{Fore.RED}{atom}{Style.RESET_ALL}")
        else:
            color_values1.append(atom)

    for atom in reagent2:
        if atom[1:] in reagent1:
            color_values2.append(f"{Fore.RED}{atom}{Style.RESET_ALL}")
        elif atom[0] != "-" and atom not in reagent1:
            color_values2.append(f"{Fore.CYAN}{atom}{Style.RESET_ALL}")
        elif atom in reagent1:
            color_values2.append(atom)

    return color_values1, color_values2


def exitus_difference(compound: list[str], exitus: list[str]) -> int:
    color_values = []

    for i, atom in enumerate(compound):
        if atom not in exitus:
            color_values.append(f"{Fore.RED}{atom}{Style.RESET_ALL}")
        elif atom in exitus and i != exitus.index(atom):
            color_values.append(f"{Fore.YELLOW}{atom}{Style.RESET_ALL}")
        else:
            color_values.append(f"{Fore.GREEN}{atom}{Style.RESET_ALL}")

    return color_values


def print_verbose_solution(
    reagents: dict, solution: list[str], exitus: list[str]
) -> None:
    compound = [atom for atom in reagents[solution[0]] if atom[0] != "-"]

    for i in range(1, len(solution)):
        colored_reagent1, colored_reagent2 = color_eliminated_atoms(
            compound, reagents[solution[i]]
        )
        print(f" {i}.\t  {' '.join(map(str, colored_reagent1))}")
        print(f"\t+ {' '.join(map(str, colored_reagent2))}")

        compound = combine_reagents(compound, reagents[solution[i]])

        print(f"\t= {' '.join(map(str, exitus_difference(compound, exitus)))}")
        print(f"\t  {' '.join(map(str, exitus))}")
        print("\n")


def validate_reagents(reagents: dict, exitus: list[str]) -> None:
    atom_pool = set(flatten(list(reagents.values())))

    for atom in exitus:
        if atom not in atom_pool:
            raise ValueError(f"Atom {atom} not found in reagents")


def bfs(
    start_sequence: dict, reagents: list[tuple], exitus: list[str], depth_limit=6
) -> list[str]:
    queue = deque(
        [
            (
                start_sequence["name"],
                start_sequence["sequence"],
                [start_sequence["name"]],
            )
        ],
    )

    while queue:
        previous_name, current_sequence, path = queue.popleft()
        if len(path) >= depth_limit:
            break

        for reagent_name, reagent_sequence, _ in reagents:
            if reagent_name == previous_name:
                continue

            new_sequence = combine_reagents(current_sequence, reagent_sequence)
            queue.append((reagent_name, new_sequence, path + [reagent_name]))

            if new_sequence == exitus:
                return path + [reagent_name]

    return None


def get_viable_start_reagents(reagents: dict, exitus: list[str]) -> dict:
    max_score = 0
    viable_starts = {}

    for reagent_name, reagent_sequence in reagents.items():
        score = 0
        i = 0

        while exitus[i] in reagent_sequence:
            score += 1
            i += 1

        if score > max_score:
            max_score = score
            viable_starts = {reagent_name: reagent_sequence}
        elif score == max_score:
            viable_starts[reagent_name] = reagent_sequence

    return viable_starts


def index_diff(atom_index: int, exitus_index: int, exitus_length: int) -> float:
    abs_index_diff = np.abs(atom_index - exitus_index)

    return 3 * (1 - abs_index_diff / exitus_length)


def score_all_reagents(reagents: dict, exitus: list[str]) -> list[tuple]:
    scored_reagents = []

    for reagent_name, reagent_sequence in reagents.items():
        score = 0

        for i in range(min(len(reagent_sequence), len(exitus))):
            try:
                exitus_index = exitus.index(reagent_sequence[i])
                score += index_diff(i, exitus_index, len(exitus))
            except ValueError:
                score -= 1

        scored_reagents.append(
            (
                reagent_name,
                reagent_sequence,
                score,
            )
        )

    scored_reagents.sort(key=lambda x: x[2], reverse=True)

    return scored_reagents
