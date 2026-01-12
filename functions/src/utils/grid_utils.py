from typing import Any, Dict, List, Tuple


def build_grid_from_buildings(
  buildings: List[Tuple[str, Dict[str, Any]]],
  category_to_id: Dict[str, int],
) -> List[List[int]]:
  # Determine grid half-size (extent)
  extent = 0
  for _, b in buildings:
    r = int(b.get("row", 0))
    c = int(b.get("col", 0))
    extent = max(extent, abs(r), abs(c))
  # per spec: use max + 1 and odd square size
  extent = extent + 1
  size = extent * 2 + 1
  grid = [[0 for _ in range(size)] for _ in range(size)]
  cy = cx = extent
  # center
  grid[cy][cx] = -1
  for _, b in buildings:
    r = int(b.get("row", 0))
    c = int(b.get("col", 0))
    cat = str(b.get("category", ""))
    val = category_to_id.get(cat, 0)
    grid[cy + r][cx + c] = val
  return grid


def grid_to_world(cy: int, cx: int, r: int, c: int) -> Tuple[int, int]:
  return (r - cy, c - cx)
