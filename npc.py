from sprite_object import *
from random import randint, random, choice 
import math
import heapq
from collections import defaultdict
import time

class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 1000
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False
        self.safe_distance = 5  # Khoảng cách an toàn tối thiểu (lưới)
        self.target_pos = None
        self.theta = 0  # Góc nhìn của NPC (dùng trong ray_cast_player_npc)
        self.path_update_timer = 0
        self.state="run"
        self.goal_Hide=None
        self.path=[]
        self.search_belief_map = [[1 for _ in range(self.game.map.rows)] for _ in range(self.game.map.cols)]
        self.lost_player_timer = 0
        self.lost_player_timeout=600
        self.current_state="tuantra"
        self.count=0

                # Q-learning parameters
        self.q_table = defaultdict(lambda: {a: 0 for a in ['up', 'down', 'left', 'right']})
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.7  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        self.known_health_points = set()  # Điểm hồi máu đã biết
        self.health_points = [(8, 3)]  # Điểm hồi máu cố định
        self.actions = ['up', 'down', 'left', 'right']
        self.last_positions  = []
        self.target_pos = None

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        # self.draw_ray_cast()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        old_pos= self.map_pos
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy
        if self.map_pos in self.health_points:
            # them vao nhan thuc cua npc
            if self.map_pos not in self.known_health_points:
                self.known_health_points.add(self.map_pos)
        

    def movement(self):
        old_pos = self.map_pos
        valid_move = True
        action = None
        # next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_pos=self.game.pathfinding.get_path_a_star(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos
        # print("di chuyen:",self.game.player.map_pos)
        # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
        if next_pos:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)
            
    def get_state(self,pos = None):
        if pos is None:
            pos = self.map_pos
        x, y = pos
        health_level = 0 if self.health < 300 else 1 if self.health < 700 else 2 # cap nhat muc do 
        return (x, y, health_level)    

    def check_health_point(self): 
        if self.map_pos in self.health_points: 
            # them vao nhan thuc cua npc
            if self.map_pos not in self.known_health_points:
                self.known_health_points.add(self.map_pos)
                # print("tim duoc diem hoi mau:",self.map_pos)
                return 200
            self.health = 1000
            return 200
        return 0
    
    def upadate_last_positions(self,pos): 
        self.last_positions.append(pos)
        if len(self.last_positions) > 15:  # nhớ 10 bước gần nhất
            self.last_positions.pop(0)

    def mahattan_distance(self,pos): 
        targets = self.known_health_points if self.known_health_points else None
        if not targets:
            return 1000
        return min(abs(pos[0] - target[0]) + abs(pos[1] - target[1]) for target in targets)

    def get_next_pos(self,pos,action): 
        x,y= pos 
        if action == 'up':
            return (x - 1, y)
        elif action == 'down':
            return (x + 1, y)
        elif action == 'left':
            return (x, y - 1)
        elif action == 'right':
            return (x, y + 1)
        return pos 
    
    def get_q_value(self, state, action):
        if not self.check_wall(state[:2][0], state[:2][1]):
            return 0
        state_puple = state
        next_pos = self.get_next_pos(state[:2], action)
        if not self.check_wall(next_pos[0], next_pos[1]):
            return float('-inf')
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in ['up', 'down', 'left', 'right']}
        # Always initialize with heuristic to ensure good starting point
        if self.q_table[state][action] == 0:  # Reinitialize if low health
            self.q_table[state][action] = -self.mahattan_distance(next_pos)
        return self.q_table[state][action]

    def get_valid_positions(self, state):
        valid_moves = [a for a in ['up', 'down', 'left', 'right'] 
               if self.check_wall(*self.get_next_pos(state[:2], a))]
        return valid_moves


    def chose_action(self, state):
        if not self.check_wall(state[:2][0], state[:2][1]):
            valid = self.get_valid_positions(state)
            return choice(valid) if valid else choice(self.actions)
        current_epsilon = max(0.01, self.epsilon * (0.995 ** self.count))
        print(f"State: {state}, Epsilon: {current_epsilon}")
        if random() < current_epsilon:
            valid_moves = self.get_valid_positions(state)
            heuristic_values = []
            if valid_moves: 
                    for a in valid_moves:
                        next_pos = self.get_next_pos(state[:2], a)
                        h = self.mahattan_distance(next_pos)
                        heuristic_values.append(h)
                    min_h = min(heuristic_values)
                    best_moves = [valid_moves[i] for i, h in enumerate(heuristic_values) if h == min_h]
                    print(f"Heuristic chosen: {best_moves}, Values: {heuristic_values}")
                    if best_moves: 
                        return choice(best_moves)
            return choice(['up', 'down', 'left', 'right'])
        q_values = [self.get_q_value(state, a) for a in ['up', 'down', 'left', 'right']]
        print(f"Q-values: {q_values}")
        valid_q_values = [q for q in q_values if q != float('-inf')]
        max_q = max(valid_q_values)
        max_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
        print(f"Max actions: {max_actions}")
        if not max_actions:
            valid_moves = [a for a in self.actions if self.check_wall(*self.get_next_pos(state[:2], a))]
            print(f"No valid Q-values, choosing random from: {valid_moves}")
            return choice(valid_moves) if valid_moves else choice(self.actions)
        return choice(max_actions)

    def get_reward(self, old_pos, new_pos,valid_move, health_reward): 
        # Tính toán phần thưởng dựa trên trạng thái cũ và mới
        reward = 0
        # Neu phat hien va cham tuong
        if not valid_move: 
            reward -= 50
        if health_reward: 
            reward += health_reward
        if self.health < 600: 
            reward -=20
        if self.health < 300: 
            reward -=20
        reward -= 1
        #         # Phần thưởng dựa trên search_belief_map (vị trí an toàn)
        # old_belief = self.search_belief_map[old_pos[0]][old_pos[1]]
        # new_belief = self.search_belief_map[new_pos[0]][new_pos[1]]
        # if new_belief < old_belief and new_belief > 0 and old_belief > 0:
        #     reward += 20  # Thưởng khi đến vị trí ít khả năng có người chơi
        if self.known_health_points:
            old_dist = self.mahattan_distance(old_pos)
            new_dist = self.mahattan_distance(new_pos)
            if new_dist < old_dist:
                reward += 50 / (new_dist + 1)
            else : 
                reward -= 50 / (old_dist + 1)
        if new_pos in self.last_positions:
            idx = self.last_positions.index(new_pos)
    # Hình phạt tăng lên cho các vị trí đã thăm gần đây hơn
            recency_factor = (len(self.last_positions) - idx) / len(self.last_positions)
            reward -= 30 * recency_factor
        return reward
    

    def update_q_table(self, old_pos,new_pos, action, health_reward, valid_move):
        self.count+=1
        print(self.count)
        state = self.get_state(old_pos)
        reward = self.get_reward(old_pos, new_pos, valid_move, health_reward)
        next_state = self.get_state(new_pos)
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in self.actions}
        self.q_table[state][action] += self.alpha * (
            reward + self.gamma * max(self.q_table[next_state].values()) - self.q_table[state][action]
        )
        self.upadate_last_positions(new_pos)
        return reward

    # def can_reach_goal(self, goal_pos):


    def Q_learning_Run(self): 
        state = self.get_state()
        action = self.chose_action(state)
        print("action:",action) 
        old_pos = self.map_pos  
        valid_move = True

        if action == 'up':
            next_pos = (self.map_pos[0] - 1, self.map_pos[1])
        elif action == 'down':
            next_pos = (self.map_pos[0] + 1, self.map_pos[1])
        elif action == 'left':
            next_pos = (self.map_pos[0], self.map_pos[1] - 1)
        elif action == 'right':
            next_pos = (self.map_pos[0], self.map_pos[1] + 1)
        next_x, next_y = next_pos
        print("next_pos:",next_pos)
        print(" truoc di chuyen:",self.map_pos)
        if self.check_wall(next_pos[0], next_pos[1]):
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)
            self.x,self.y = next_x, next_y
            time.sleep(0.1)  # Thêm delay 0.5 giây để quan sát chuyển vị trí
        if not self.check_wall(self.map_pos[0], self.map_pos[1]):
                valid_move = False
                # Kiểm tra điểm hồi máu
        print(" sau di chuyen:",self.map_pos)
        health_reward = self.check_health_point()
                # Tính phần thưởng
        reward = self.get_reward(old_pos, self.map_pos, valid_move, health_reward)
                # Cập nhật Q-table
        next_state = self.get_state()
        if (self.known_health_points or health_reward) and action and old_pos != next_pos:
            self.update_q_table(old_pos, self.map_pos, action, health_reward, valid_move)
        self.epsilon = max(0.01, self.epsilon * 0.995)

    # Cap nhat belief map dua vao ket qua hanh dong
    def update_search_belief_map(self):
            # Neu nhin thay dich
            check_see=self.ray_cast_player_npc()
            if check_see:
                plyer_pos=self.game.player.map_pos
                fov_radius = 4
                for x in range(self.game.map.cols):
                    for y in range(self.game.map.rows):
                        if (x,y) in self.game.map.world_map:
                            continue
                        self.search_belief_map[x][y] = 0

                for x in range(max(0, plyer_pos[0] - 2*fov_radius), min(self.game.map.cols, plyer_pos[0] + 2*fov_radius)):
                    for y in range(max(0, plyer_pos[1] - 2*fov_radius), min(self.game.map.rows, plyer_pos[1] + 2*fov_radius)):
                            # tanng niem tin sieu to
                            if (x,y) in self.game.map.world_map:
                                continue
                            self.search_belief_map[x][y] +=5
                            # print("resset:",x,y)
                for x in range(max(0, plyer_pos[0] - fov_radius), min(self.game.map.cols, plyer_pos[0] + fov_radius)):
                    for y in range(max(0, plyer_pos[1] - fov_radius), min(self.game.map.rows, plyer_pos[1] + fov_radius)):
                            # tanng niem tin sieu to
                            if (x,y) in self.game.map.world_map:
                                continue
                            self.search_belief_map[x][y] +=5
                            # print("resset:",x,y)
            else:
                fov_radius = 2
                for x in range(max(0, self.map_pos[0] - fov_radius), min(self.game.map.cols, self.map_pos[0] + fov_radius)):
                    for y in range(max(0, self.map_pos[1] - fov_radius), min(self.game.map.rows, self.map_pos[1] + fov_radius)):
                            # giam niem tin
                            if (x,y) in self.game.map.world_map:
                                continue
                            self.search_belief_map[x][y] = 0
                            # print("resset:",x,y)
                            

    # sau moi hanh dong cap nhat lai niem tin
    def decay_search_belief_map(self): 
            for x in range(self.game.map.cols):
                for y in range(self.game.map.rows):
                        self.search_belief_map[x][y] = self.search_belief_map[x][y] + 0.01

    # tim vi tri co niem tin xuat hien dich cao nhat 
    def find_patroltarget_belief_map(self): 
        best_score=-float("inf")
        best_pos=None
        max_belief = max(self.search_belief_map[x][y] 
                 for x in range(self.game.map.cols) 
                 for y in range(self.game.map.rows) 
                 if (x, y) not in self.game.map.world_map)
        max_distance = math.sqrt((self.game.map.rows**2 + self.game.map.cols**2))
        for x in range(self.game.map.cols):
            for y in range(self.game.map.rows):
                if (x,y) in self.game.map.world_map:
                    continue
                belief = self.search_belief_map[x][y]
                dist=math.sqrt((x-self.map_pos[0])**2 + (y-self.map_pos[1])**2)
                # Tính điểm: ưu tiên những điểm xa npc và có niềm tin cao
                score= belief/max_belief * 0.95 - dist/max_distance*0.05
                # self.search_belief_map[x][y] = score
                if score > best_score:
                    best_score = score
                    best_pos = (x, y)
        if not best_pos: 
            valid_positions = [(x,y) for x in range(self.game.map.cols) for y in range(self.game.map.rows) 
                               if (x,y) not in self.game.map.world_map and (x,y) != self.map_pos]
            index = randint(0, len(valid_positions)-1)
            best_pos = valid_positions[index]
        return best_pos

    # Thuc hien di tuan dua vao niem tin da co
    def tuan_tra(self):
        best_pos = self.find_patroltarget_belief_map()
        valid_move = True
        action = None
        if best_pos:
            old_pos = self.map_pos
            next_pos=self.game.pathfinding.get_path_a_star(self.map_pos, best_pos)
            next_x, next_y = next_pos
            # print("di chuyen:",self.game.player.map_pos)
            # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
            if next_pos:
                angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
                dx = math.cos(angle) * self.speed
                dy = math.sin(angle) * self.speed
                self.check_wall_collision(dx, dy)
               

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def heuristic_state(self,state,goal_state): 
        # chi phi khoang cach
        max_distance=math.sqrt(self.game.map.cols**2 + self.game.map.rows**2)
        distance_cost=0
        distance_current=math.sqrt((self.map_pos[0]-self.game.player.map_pos[0])**2 + (self.map_pos[1]-self.game.player.map_pos[1])**2)
        if state == 'attack' or state == 'movement':
            distance_cost =   distance_current# Gần player khi tấn công hoặc di chuyển
        elif state == 'escape' or state=="hide":
            distance_cost = max_distance - distance_current  # Xa player khi chạy trốn
        normalized_distance_cost=distance_cost/max_distance
        distance_penalty=0

        if distance_current <=self.attack_dist: 
            if state in ['attack']: 
                distance_penalty=0.2
            elif state in ['hide']: 
                distance_penalty=1.0
            elif state in ['escape']: 
                distance_penalty=0.4
            else: 
                distance_penalty=0.8
        else: 
            if state in ['attack']: 
                distance_penalty=0.3
            elif state in ['hide']: 
                distance_penalty=0.2
            elif state in ['escape']:
                distance_penalty=0.3
            else: 
                distance_penalty=0.4


        # chi phi dua vao luong mau mat di 
        npc_health_lost= 1000 - self.health
        normalized_health__loss_cost=npc_health_lost/1000
        if self.health <600 and self.health >=300: 
            if state in ['attack']: 
                health_penalty=0.2
            elif state  in ['escape']:
                health_penalty=0
            elif state in ['hide']: 
                health_penalty=0.3
            else : 
                health_penalty=0.8
            # distance_penalty = 0.2 if state in ['escape','hide'] else 0.5
        elif self.health <300:
            if state in ['attack']: 
                health_penalty=0
                # distance_penalty=0.3
            elif state  in ['escape','hide']:
                health_penalty=0.3
                # distance_penalty=0
            else : 
                health_penalty=0.8
                # if state in ['movement']: 
                #     distance_penalty=0.1
                # else : 
                #     distance_penalty=0.5

        see_player=0

        if self.ray_cast_player_npc(): 
            if state in ['escape','movement']: 
                see_player=0
            else : 
                see_player=0.4
        else: 
            if state in ['escape']: 
                see_player=0.2
            elif state in ['hide']:
                see_player=0.1
            else: 
                see_player =1


        # Chi phi dua tren chuyen trang thai 
        state_cost = 0.0
        # if state != goal_state:
        if goal_state == "movement":
            state_cost = 0.2 if state == "attack" else 0.2 if state == "escape" else 0.8 if state == "hide" else 0.5
        elif goal_state == "attack":
            state_cost = 0.2 if state == "movement" else 0.2 if state == "escape" else 0.8 if state == "hide" else 0.5
        elif goal_state == "escape":
            state_cost = 0.2 if state in ["attack", "hide"] else 0.5 if state == "movement" else 0.5
        elif goal_state == "hide":
            state_cost = 0.2 if state == "escape" else 0.5 if state == "movement" else 0.8 if state == "attack" else 0.2

        w_distance = 0.25
        w_health_loss = 0.3
        w_see = 0.25
        w_state = 0.2

        total_cost = (
        w_distance * (normalized_distance_cost + distance_penalty)+
        w_health_loss * (1 - normalized_health__loss_cost + health_penalty) +
        w_state * state_cost + 
        w_see * see_player
        )

        return total_cost


    def leo_doi(self,current_state,goal_state='hide'): 
        print(current_state)
            # Các trạng thái hành vi có thể có
        possible_states = ['attack', 'escape', 'movement', 'hide']

            # Chi phí chuyển đổi giữa các trạng thái
        transition_costs = {
            ('attack', 'escape'): 0.2, ('attack', 'movement'): 0.5, ('attack', 'hide'): 0.8, ('attack','attack') : 0.2,
            ('escape', 'attack'): 0.2, ('escape', 'movement'): 0.8, ('escape', 'hide'): 0.2, ('escape','escape') : 0.2,
            ('movement', 'attack'): 0.2, ('movement', 'escape'): 0.5, ('movement', 'hide'): 0.8, ('movement','movement') : 0.2,
            ('hide', 'attack'): 0.8, ('hide', 'escape'): 0.2, ('hide', 'movement'): 0.8, ('hide','hide') : 0.3
        }
        best_state=current_state
        best_cost=transition_costs.get((current_state,current_state),1.0) + self.heuristic_state(current_state,goal_state)
        for next_state in possible_states: 
            new_cost=transition_costs.get((current_state,next_state),1.0) + self.heuristic_state(next_state,goal_state)
            if new_cost < best_cost: 
                best_cost=new_cost
                best_state=next_state
        return best_state


    def run_logic(self):
        if self.alive:
            self.ray_cast_value= self.ray_cast_player_npc()
            self.check_hit_in_npc()
            self.update_search_belief_map()
            if self.pain:
                self.animate_pain()
            # Neu nhin thay dich
            elif self.ray_cast_value:
                # self.update_search_belief_map()
                # Bat che do tan cong
                self.player_search_trigger = True
                
                # Neu co mau thap thi bo chay
                if self.health < 600:
                    self.animate(self.walk_images) # Chạy trốn
                    next_current=self.leo_doi(self.current_state)
                    self.current_state=next_current
                    if next_current=='attack': 
                        self.animate(self.attack_images)
                        if self.dist < self.attack_dist and self.ray_cast_player_npc():
                            self.attack()
                        else: 
                            # self.bo_chay()
                            print()
                        print("tan cong")
                    elif next_current=='movement': 
                        self.animate(self.walk_images)
                        self.movement()
                        print("duoi theo")
                    elif next_current=='escape': 
                        self.animate(self.walk_images)
                        if len(self.known_health_points) > 0: 
                            if self.target_pos is None:
                                self.Q_learning_Run()
                            else: 
                                # self.move_towards_target()
                                self.Q_learning_Run()

                            print("chay theo Q")
                        else : 
                            self.bo_chay()
                            print("bo chay")
                    elif next_current=='hide': 
                        print("an tron")
                
                # Neu player o trong tam tan cong va mau du nhieu
                elif self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                    self.current_state="attack"
                
                # Neu khoang cach khong du tam ban, thi di chuyen lai gan hon
                else:
                    self.animate(self.walk_images)
                    self.movement()
                    self.current_state="movement"

            # Neu khong nhin thay player, nhung da xac dinh duoc muc tieu
            else:
                self.player_search_trigger=False
                 # Neu co mau thap thi bo chay
                if self.health < 600:
                    self.animate(self.walk_images) # Chạy trốn
                    # self.bo_chay()
                    # self.current_state='escape'
                    next_current=self.leo_doi(self.current_state)
                    self.current_state=next_current
                    if next_current=='attack': 
                        self.animate(self.attack_images)
                        if self.dist < self.attack_dist and self.ray_cast_player_npc():
                            self.attack()
                        else: 
                            # self.bo_chay()
                            print()
                        print("tan cong")
                    elif next_current=='movement': 
                        self.animate(self.walk_images)
                        self.movement()
                        print("duoi theo")
                    elif next_current=='escape': 
                        self.animate(self.walk_images)
                        # self.bo_chay()
                        if len(self.known_health_points) > 0: 
                            if self.target_pos is None:
                                self.Q_learning_Run()
                            else: 
                                # self.move_towards_target()
                                self.Q_learning_Run()
                            print("chay theo Q")
                        else : 
                            self.bo_chay()
                            print("bo chay")
                        
                    elif next_current=='hide': 
                        print("an tron")
                
                # Neu khoang cach khong du tam ban, thi di chuyen lai gan hon
                else :   
                    self.animate(self.walk_images)
                    # self.movement()
                    self.decay_search_belief_map()
                    self.tuan_tra()

        else:
            self.animate_death()


    def bo_chay(self):
        """
        NPC chạy đến góc bản đồ xa nhất so với người chơi.
        """
        self.health+=0.05
        player_map_pos=self.game.player.map_pos
        current_pos = self.map_pos
        # Kiểm tra xem NPC có thấy player không
        if self.state=="run": 
            player_in_sight= self.ray_cast_player_npc()

            if not player_in_sight:
                # print("hide")
                self.state="hide"
                # Tìm góc xa nhất
                max_dist=self.find_farthest_corner( player_map_pos)
                next_pos = self.game.pathfinding.get_path(self.map_pos, max_dist)
                next_x, next_y = next_pos

                # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
                if next_pos :
                    angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
                    dx = math.cos(angle) * self.speed
                    dy = math.sin(angle) * self.speed
                    self.check_wall_collision(dx, dy)
                return
            else : 
                # print("run")
                # Cập nhật timer, nhưng tăng tần suất nếu vẫn bị nhìn thấy
                self.path_update_timer += self.game.delta_time
                update_interval = 0.5 if not player_in_sight else 0.2
                if self.path_update_timer < 0.5 and self.target_pos:
                    next_pos = self.target_pos
                else:
                    self.path_update_timer = 0
                    # Tìm vị trí an toàn nhất để NPC chạy trốn khỏi người chơi
                    next_pos = self.find_safe_position(player_map_pos)
                    if not next_pos:
                        # Nếu không tìm thấy vị trí an toàn, chọn vị trí ngẫu nhien
                        self.random_move()
                        return
                    self.target_pos = next_pos
                # Tính toán đường đi bằng A* pathfinding 
                # Di chuyển đến next_pos
                if next_pos :
                    next_x, next_y = next_pos
                    target_x = next_x + 0.5  # Tâm ô (đơn vị ô)
                    target_y = next_y + 0.5
                    angle = math.atan2(target_y - self.y, target_x - self.x)
                    dx = math.cos(angle) * self.speed
                    dy = math.sin(angle) * self.speed
                    self.check_wall_collision(dx, dy)

                    # # Nếu gần tường và thấy player, ẩn nấp
                    if self.is_near_wall() and player_in_sight:
                        self.state="hide"
                        print("hide")
                        self.theta = angle  # Xoay để đối mặt tường
                        return  # Dừng di chuyển để giả lập ẩn nấp
            
        elif self.state=="hide":
            # self.current_state="hide"
            # print(" state :hide")
            map_width = self.game.map.cols - 1  # Trừ 1 vì tọa độ bắt đầu từ 0
            map_height = self.game.map.rows - 1

            # Định nghĩa 4 góc: trên-trái, trên-phải, dưới-trái, dưới-phải
            corners = [
                (1, 1),              # Góc trên-trái
                (map_width -1, 1),      # Góc trên-phải
                (1, map_height-1),     # Góc dưới-trái
                (map_width-1, map_height-1)  # Góc dưới-phải
            ]
            # print('Truoc khi di chuyen:',self.map_pos)
            for corner in corners:
                if corner==self.map_pos:
                    self.state="run"
                    self.path=[]
                    print("da den")
                    self.goal_Hide=None
                    return 
            if self.goal_Hide==None:
                max_dist=self.find_farthest_corner( player_map_pos)
                self.goal_Hide=max_dist
            next_pos=self.game.pathfinding.get_path(self.map_pos, self.goal_Hide)
            # print("dich:",self.goal_Hide)
            next_x, next_y = next_pos
            # print('sau khi di chuyen',next_pos)
                # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
            if next_pos :
                    angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
                    dx = math.cos(angle) * self.speed
                    dy = math.sin(angle) * self.speed
                    # print("di chuyen")
                    self.check_wall_collision(dx, dy)
                    # print('da di chuyen:',self.map_pos)


    def find_farthest_corner(self, player_map_pos):
        """
        Tìm vị trí trong 4 góc bản đồ xa player nhất, đảm bảo không có tường và có đường đi.
        """
        map_width = self.game.map.cols - 1  # Trừ 1 vì tọa độ bắt đầu từ 0
        map_height = self.game.map.rows - 1

        # Định nghĩa 4 góc: trên-trái, trên-phải, dưới-trái, dưới-phải
        corners = [
            (1, 1),              # Góc trên-trái
            (map_width -1, 1),      # Góc trên-phải
            (1, map_height-1),     # Góc dưới-trái
            (map_width-1, map_height-1)  # Góc dưới-phải
        ]

        best_corner = None
        max_distance = -float('inf')

        current_pos = self.map_pos

        for corner in corners:
            # Kiểm tra xem góc có nằm trong tường không
            if corner in self.game.map.world_map:
                continue
            # Tính khoảng cách từ player đến góc
            dist = (corner[0] - player_map_pos[0]) ** 2 + (corner[1] - player_map_pos[1]) ** 2
            # Chọn góc xa nhất
            if dist > max_distance:
                max_distance = dist
                best_corner = corner

        return best_corner


    def random_move(self):
        """
        Di chuyển ngẫu nhiên nếu không tìm được đường đi.
        """
        ways = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4 hướng
        random.shuffle(ways)
        for dx, dy in ways:
            new_x, new_y = self.map_pos[0] + dx, self.map_pos[1] + dy
            new_pos = (new_x, new_y)
            if (new_pos not in self.game.map.world_map and 
                new_pos not in self.game.object_handler.npc_positions):
                self.x = new_x + 0.5
                self.y = new_y + 0.5
                break


    def find_safe_position(self, player_map_pos):
        """
        Tìm vị trí xa player nhất trên lưới, đảm bảo ngoài tầm nhìn.
        """
        map_width = self.game.map.cols
        map_height = self.game.map.rows
        best_pos = None
        max_distance = -float('inf')

        # Kiểm tra các ô trong bán kính 10 ô
        x_start = max(0, self.map_pos[0] - 10)
        x_end = min(map_width, self.map_pos[0] + 11)
        y_start = max(0, self.map_pos[1] - 10)
        y_end = min(map_height, self.map_pos[1] + 11)

        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                pos = (x, y)
                if pos in self.game.map.world_map:  # Bỏ qua tường
                    continue
                dist = math.hypot(x - player_map_pos[0], y - player_map_pos[1])

                # Kiểm tra line-of-sight từ player đến vị trí này
                in_line_of_sight = self.check_player_line_of_sight(pos)

                # Chỉ chọn vị trí ngoài tầm nhìn
                if in_line_of_sight:
                    continue

                # Tính điểm: ưu tiên xa player
                score = dist
                if dist >= self.safe_distance and score > max_distance:
                    max_distance = score
                    best_pos = pos

        return best_pos

    def check_player_line_of_sight(self, target_pos):
        """
        Kiểm tra xem target_pos có trong tầm nhìn của player không.
        """
        if self.game.player.map_pos == target_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == target_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == target_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    def is_near_wall(self):
        """
        Kiểm tra xem NPC có gần tường không.
        """
        ox, oy = self.x, self.y
        x_map, y_map = self.map_pos
        ray_angle = self.theta
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # Horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a
        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor in self.game.map.world_map:
                if depth_hor <= 1.0:
                    return True
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # Verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a
        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert in self.game.map.world_map:
                if depth_vert <= 1.0:
                    return True
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        return False

    def random_move(self):
        """
        Di chuyển ngẫu nhiên nếu không tìm được đường đi.
        """
        ways = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(ways)
        for dx, dy in ways:
            new_x, new_y = self.map_pos[0] + dx, self.map_pos[1] + dy
            new_pos = (new_x, new_y)
            if (new_pos not in self.game.map.world_map and 
                new_pos not in self.game.object_handler.npc_positions):
                self.x = new_x + 0.5
                self.y = new_y + 0.5
                break

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    def is_visible(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        npc_dist_v, npc_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos
        tx, ty = self.map_pos

        ray_angle = math.atan2(ty - oy, tx - ox)

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # HORIZONTAL CHECK
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for _ in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                npc_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # VERTICAL CHECK
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for _ in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                npc_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        npc_dist = max(npc_dist_v, npc_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < npc_dist < wall_dist or not wall_dist:
            # Góc nhìn phải hợp lệ nữa
            delta_angle = ray_angle - self.game.player.angle
            delta_angle = (delta_angle + math.pi) % (2 * math.pi) - math.pi
            if abs(delta_angle) < HALF_FOV:
                return True

        return False

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y),
                         (100 * self.x, 100 * self.y), 2)


class SoldierNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)

# class CacoDemonNPC(NPC):
#     def __init__(self, game, path='resources/sprites/npc/caco_demon/0.png', pos=(10.5, 6.5),
#                  scale=0.7, shift=0.27, animation_time=250):
#         super().__init__(game, path, pos, scale, shift, animation_time)
#         self.attack_dist = 1.0
#         self.health = 150
#         self.attack_damage = 25
#         self.speed = 0.05
#         self.accuracy = 0.35

class CyberDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/cyber_demon/0.png', pos=(11.5, 6.0),
                 scale=1.0, shift=0.04, animation_time=210):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 350
        self.attack_damage = 15
        self.speed = 0.055
        self.accuracy = 0.25