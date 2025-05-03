from collections import deque
from functools import lru_cache
from math import sqrt
import heapq

class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.mini_map
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        self.graph = {}
        self.get_graph()

    @lru_cache
    def get_path(self, start, goal):
        self.visited = self.bfs(start, goal, self.graph)
        path = [goal]
        step = self.visited.get(goal, start)

        while step and step != start:
            path.append(step)
            step = self.visited[step]
        return path[-1]
    
    @lru_cache
    def get_path_all(self, start, goal):
        self.visited = self.bfs(start, goal, self.graph)
        path = [goal]
        step = self.visited.get(goal, start)

        while step and step != start:
            path.append(step)
            step = self.visited[step]
        return path[::-1] 

    def bfs(self, start, goal, graph):
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            next_nodes = graph[cur_node]

            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited



    def get_next_nodes(self, x, y):
        return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.game.map.world_map]

    def get_graph(self):
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)

    def huristic(self, a, b):
        return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
    
    def a_star(self, start, goal,graph):
        """A* algorithm for pathfinding"""
        open_set=[]
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.huristic(start, goal)}

        while open_set: 
            _,current = heapq.heappop(open_set)
            if current == goal:
                return self.reconstruct_path(came_from, current)
            next_nodes = graph[current]
            for next_node in next_nodes:
                tentative_g_score = g_score[current] + 1
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current
                    g_score[next_node] = tentative_g_score
                    f_score[next_node] = tentative_g_score + self.huristic(next_node, goal)
                    heapq.heappush(open_set, (f_score[next_node], next_node))
        return None

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def get_path_a_star(self, start, goal):
        path = self.a_star(start, goal, self.graph)
        if not path or len(path) < 2:
            return start  # Không có đường đi hoặc đã ở goal
        return path[1]   # Trả về bước kế tiếp sau start


