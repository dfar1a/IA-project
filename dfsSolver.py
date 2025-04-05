from utils import is_solved, get_state_hash
import copy


def dfs_limited(game, max_depth, visited, path, depth_level=0):
    indent = "  " * depth_level  # para debug visual
    print(f"{indent}🔍 DFS depth={max_depth}, path_len={len(path)}")

    if is_solved(game.board):
        print(f"{indent}✅ Solução encontrada!")
        return path

    if max_depth == 0:
        return None

    state_hash = get_state_hash(game.board)
    if state_hash in visited:
        return None
    visited.add(state_hash)

    for i, col in enumerate(game.board.columns):
        if col.is_empty():
            continue
        card = col.top()

        # Tenta coluna → coluna
        for j in range(len(game.board.columns)):
            if i == j:
                continue
            new_game = copy.deepcopy(game)
            if new_game.move_card(i, j):
                print(f"{indent}➡️ {card} de coluna {i} para coluna {j}")
                result = dfs_limited(
                    new_game,
                    max_depth - 1,
                    visited.copy(),
                    path + [((i, j), card)],
                    depth_level + 1,
                )
                if result:
                    return result

        # Tenta coluna → foundation
        for f, foundation in enumerate(game.board.foundations):
            new_game = copy.deepcopy(game)
            if new_game.move_card_to_foundation(i, f):
                print(f"{indent}🏛️ {card} de coluna {i} para fundação {f}")
                result = dfs_limited(
                    new_game,
                    max_depth - 1,
                    visited.copy(),
                    path + [((i, f), card)],
                    depth_level + 1,
                )
                if result:
                    return result

    return None


def dfs_solver(initial_game):
    depth = 1
    while depth < 100:
        print(f"\n🔁 Tentativa com profundidade {depth}")
        visited = set()
        result = dfs_limited(copy.deepcopy(initial_game), depth, visited, [], 0)
        if result is not None:
            print(f"🎯 Solução encontrada com profundidade {depth}!")
            return result
        depth += 1
    print("❌ Nenhuma solução encontrada")
    return None
