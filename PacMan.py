import os
import time
import msvcrt
import random
import enum

gamefield_template = ["╔════════════════════╦═══════╗",
                      "║☺•••••••••••••••••••║•••••••║",
                      "╠═════╗•╔═══╗•╔═════•║•════╗•║",
                      "║•••••║•║   ║•║•••••☻••••••║•║",
                      "║•════╝•╚═══╝•╚═════•╚═════╝•║",
                      "║•••••••••••☻••••••••••••••••║",
                      "╚════════════════════════════╝"]

all_possible_fields = ["╔", "╗", "╚", "╝", "═", "║", "╠", "╣", "╦", "╩", "╬", "•", "☺", " ", "☻"]
passable_fields = ["•", " "]

# 2D vector class for componentwise mathematical operations
class Vec2D:
    
    # iterator for x and y coordinates
    class Vec2DIterator:
        def __init__(self, other):
            self._n = 0
            self._other = other
        
        def __iter__(self):
            return self
        
        def __next__(self):
            self._n += 1
            
            if self._n > 2:
                raise StopIteration
            elif self._n == 1:
                return self._other.x
            else:
                return self._other.y

    def __iter__(self):
        return self.Vec2DIterator(self)
    
    def __init__(self, x = 0.0, y = 0.0):
        if not ((type(x) == int or type(x) == float) or (type(y) == int or type(y) == float)):
            raise BaseException("Invalid type", type(x), type(y))
        
        self.x = x
        self.y = y
        
    def __add__(self, other):
        if type(other) == list:
            return Vec2D(self.x + other[0], self.y + other[1])
        elif type(other) == Vec2D:
            return Vec2D(self.x + other.x, self.y + other.y)
        else:
            raise BaseException("Invalid type", type(other))
    
    def __sub__(self, other):
        if type(other) == list:
            return Vec2D(self.x - other[0], self.y - other[1])
        elif type(other) == Vec2D:
            return Vec2D(self.x - other.x, self.y - other.y)
        else:
            raise BaseException("Invalid type", type(other))
        
    def __eq__(self, other):
        if type(other) == list:
            return len(other) == 2 and self.x == other[0] and self.y == other[1]
        elif type(other) == Vec2D:
            return self.x == other.x and self.y == other.y
        else:
            raise BaseException("Invalid type", type(other))
        
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    
class Options:
    class Flags(enum.Flag):
        pass

class Direction(enum.Enum):
    WEST = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3
    NONE = 4
    
class Field:
    SYMBOL = str()
    
class Food(Field):
    SYMBOL = "•"
    
class Movable(Field):
    def __init__(self, starting_position = Vec2D()):
        assert(type(starting_position) == Vec2D)
        self.position = starting_position
        self.direction = Direction.EAST
        
class PacMan(Movable):
    SYMBOL = "☺"
    
    def __init__(self, starting_position = Vec2D()):
        super().__init__(starting_position)
        
class Enemy(Movable):
    SYMBOL = "☻"
    
    def __init__(self, starting_position = Vec2D()):
        super().__init__(starting_position)
    

class Gamefield:
    def __init__(self):
        self.reset()
        
    # resets the gamefield to an empty gamefield with one PacMan, no enemies, no walls, no food, ...
    def reset(self):
        self.gamefield = []
        self.user_input_direction = Direction.NONE
        self.n_initial_food_fields = 0
        self.pacman = PacMan()
        self.enemies = []
        
    def init_from_template(self, template):
        self.reset()
        self.make_gamefield_from_template(template)
        
        for z in range(0, len(self.gamefield)):
            for s in range(0, len(self.gamefield[z])):
                if type(self.gamefield[z][s]) == str:
                    # find starting position for PacMan
                    if self.gamefield[z][s] == PacMan.SYMBOL:
                        # reset field
                        self.gamefield[z][s] = Food.SYMBOL
                        
                        self.pacman = PacMan(Vec2D(z,s))
                    # count food-fields
                    elif self.gamefield[z][s] == Food.SYMBOL:
                        self.n_initial_food_fields += 1
                    # initialize enemy-objects
                    elif self.gamefield[z][s] == Enemy.SYMBOL:
                        # reset field
                        self.gamefield[z][s] = Food.SYMBOL
                        
                        new_enemy = Enemy()
                        new_enemy.position = Vec2D(z,s)
                        
                        # randomize starting direction of enemies
                        possible_directions = self.get_all_passable_directions_around(new_enemy.position)
                        new_enemy.direction = possible_directions[random.randint(0, len(possible_directions)-1)]
                        
                        self.enemies.append(new_enemy)
                        
        self.n_current_food_fields = self.n_initial_food_fields
        
    # load a gamefield from a file, reset the current gamefield
    def load_from_file(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as file:
            self.reset()
            
            template = []
            for line in file:
                line = line.rstrip("\n")
                template.append(line)
                
            self.init_from_template(template)
        
    # TODO: Do I need this?
    def make_gamefield_from_template(self, template):
        for z in range(0, len(template)):
            self.gamefield.append([])
            for templ_field in template[z]:
                self.gamefield[z].append(templ_field)
    
    # print the gamefield
    def print(self):
        for z in range(0,len(self.gamefield)):
            line = ""
            for s in range(0,len(self.gamefield[z])):
                
                if self.pacman.position == [z,s]:
                    line += PacMan.SYMBOL
                else:
                    enemy_printed = False
                    for enemy in self.enemies:
                        if enemy.position.x == z and enemy.position.y == s:
                            line += Enemy.SYMBOL
                            enemy_printed = True
                            break
                        
                    if not enemy_printed:
                        line += self.gamefield[z][s]
                
            print(line.center(120))
            
    # get all directions a pawn on the position could move
    def get_all_passable_directions_around(self, position: Vec2D) -> list:
        passable_directions = []
        
        for i in range(0,4):
            if self.get_field_direction_of(position, Direction(i)) in passable_fields:
                passable_directions.append(Direction(i))
                
        return passable_directions
            
    def get_field_by_position(self, position: Vec2D) -> str:
        return self.gamefield[position.x][position.y]
    
    def get_position_west_of(self, position: Vec2D) -> Vec2D:
        return position + [0,-1]
    
    def get_position_east_of(self, position: Vec2D) -> Vec2D:
        return position + [0,1]
    
    def get_position_north_of(self, position: Vec2D) -> Vec2D:
        return position + [-1,0]
    
    def get_position_south_of(self, position: Vec2D) -> Vec2D:
        return position + [1,0]
    
    # get the next position in the direction of the parameter direction
    def get_position_direction_of(self, position: Vec2D, direction: Direction) -> Vec2D:
        if direction == Direction.WEST:
            return self.get_position_west_of(position)
        elif direction == Direction.EAST:
            return self.get_position_east_of(position)
        elif direction == Direction.NORTH:
            return self.get_position_north_of(position)
        elif direction == Direction.SOUTH:
            return self.get_position_south_of(position)
    
    def get_field_west_of(self, position: Vec2D) -> str:
        return self.gamefield[position.x][position.y-1]
    
    def get_field_east_of(self, position: Vec2D) -> str:
        return self.gamefield[position.x][position.y+1]
    
    def get_field_north_of(self, position: Vec2D) -> str:
        return self.gamefield[position.x-1][position.y]
    
    def get_field_south_of(self, position: Vec2D) -> str:
        return self.gamefield[position.x+1][position.y]
    
    # get the next field string in the direction of the parameter direction
    def get_field_direction_of(self, position: Vec2D, direction: Direction) -> str:
        if direction == Direction.WEST:
            return self.get_field_west_of(position)
        elif direction == Direction.EAST:
            return self.get_field_east_of(position)
        elif direction == Direction.NORTH:
            return self.get_field_north_of(position)
        elif direction == Direction.SOUTH:
            return self.get_field_south_of(position)
    
    # returns number of columns of gamefield
    def n_columns(self) -> int:
        return len(self.gamefield[0])
    
    # returns number of rows of gamefield
    def n_rows(self) -> int:
        return len(self.gamefield)
    
    # finds clockwise a new field for a pawn, randomizes direction on junctions or not
    def find_free_field_clockwise(self, initial_direction: Direction, initial_position: Vec2D, randomizeDirection = False):
        directions = [Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH]
        current_index = initial_direction.value
        
        possible_directions = []
        
        # check clockwise all fields around the pawn if they are passable. If yes, add them to list.
        for i in range(0,4):
            for j in range(0,4):
                if directions[current_index] == Direction(j) and self.get_field_direction_of(initial_position, Direction(j)) in passable_fields:
                    possible_directions.append(Direction(j))
            current_index += 1
        
        if len(possible_directions) == 1:
            return [self.get_position_direction_of(initial_position, possible_directions[0]), possible_directions[0]]
            
        if not randomizeDirection:
            # find first direction clockwise that is not the opposite direction of the current direction of PacMan
            for d in possible_directions:
                if d == Direction.WEST and initial_direction == Direction.EAST\
                or d == Direction.EAST and initial_direction == Direction.WEST\
                or d == Direction.NORTH and initial_direction == Direction.SOUTH\
                or d == Direction.SOUTH and initial_direction == Direction.NORTH:
                    continue
                else:
                    return [self.get_position_direction_of(initial_position, d), d]
        else:
            # find all directions clockwise that are not the opposite direction of the current direction and get a random one
            all_non_opposites = []
            
            for d in possible_directions:
                if d == Direction.WEST and initial_direction == Direction.EAST\
                or d == Direction.EAST and initial_direction == Direction.WEST\
                or d == Direction.NORTH and initial_direction == Direction.SOUTH\
                or d == Direction.SOUTH and initial_direction == Direction.NORTH:
                    continue
                else:
                    all_non_opposites.append([self.get_position_direction_of(initial_position, d), d])
                    
            return all_non_opposites[random.randint(0, len(all_non_opposites)-1)]
                
        return [self.get_position_direction_of(initial_position, possible_directions[0]), possible_directions[0]]
    
    # get the next position of a pawn (PacMan or enemy) depending on it's current position, direction and whether to
    # randomize the direction on junctions (usually true for enemies) or not (usually false for PacMan)
    def get_next_pawn_position(self, position: Vec2D, direction: Direction, randomizeDirection = False):
        # get the next position depending on the direction of pawn
        next_position = self.get_position_direction_of(position, direction)
        
        # if the next position is not passable, find a free field to move
        if not self.get_field_by_position(next_position) in passable_fields:
            free_field_result = self.find_free_field_clockwise(direction, position, randomizeDirection)
            next_position = free_field_result[0]
            next_direction = free_field_result[1]
            
            return [next_position, next_direction]
        else:
            # if there is a junction, go straight ahead or select a random direction depending on randomizeDirection
            if randomizeDirection:
                # if there are other ways possible than straight ahead or back, select a random direction
                possible_directions = self.get_all_passable_directions_around(position)
                
                if len(possible_directions) > 2:
                    all_non_opposites = []
                    
                    for d in possible_directions:
                        if d == Direction.WEST and direction == Direction.EAST\
                        or d == Direction.EAST and direction == Direction.WEST\
                        or d == Direction.NORTH and direction == Direction.SOUTH\
                        or d == Direction.SOUTH and direction == Direction.NORTH:
                            continue
                        else:
                            all_non_opposites.append([self.get_position_direction_of(position, d), d])
                            
                    return all_non_opposites[random.randint(0, len(all_non_opposites)-1)]
                else:
                    # if there are only two possible directions, one is back and one is straight ahead, so go ahead
                    return [next_position, direction]
            else:
                return [next_position, direction]
        
    # check if there is an enemy on the position
    def is_enemy_on_position(self, position: Vec2D) -> bool:
        for enemy in self.enemies:
            if enemy.position == position:
                return True
        
        return False
        
    # move all enemies for one field
    def move_enemies(self):
        for enemy in self.enemies:
            next_position_direction = self.get_next_pawn_position(enemy.position, enemy.direction, True)
            next_position = next_position_direction[0]
            next_direction = next_position_direction[1]

            if self.pacman.position == next_position:
                game_over()
                
            enemy.position = next_position
            enemy.direction = next_direction

    # make one step in the game. Move PacMan, eat food, move enemies, check for collision with PacMan, ...
    def step(self):
        self.gamefield[self.pacman.position.x][self.pacman.position.y] = " "
        next_position = []
        
        # if there has been an user input
        if self.user_input_direction != Direction.NONE:
            # check if the user input is valid. No walls in the way etc.
            if self.get_field_direction_of(self.pacman.position, self.user_input_direction) in passable_fields:
                self.pacman.direction = self.user_input_direction
                self.user_input_direction = Direction.NONE

        # get the next position (and orientation) depending on the direction of PacMan
        next_pawn_step = self.get_next_pawn_position(self.pacman.position, self.pacman.direction)
        next_position = next_pawn_step[0]
        next_direction = next_pawn_step[1]
        
        if self.is_enemy_on_position(next_position):
            game_over()
        elif self.get_field_by_position(next_position) == Food.SYMBOL:
            self.n_current_food_fields -= 1
            if self.n_current_food_fields == 0:
                won()
        
        self.pacman.position = next_position
        self.pacman.direction = next_direction
        
        self.move_enemies()
                            
gamefield = Gamefield()
speed = 0.1

# called if PacMan is dead
def game_over():
    print("Du hast leider verloren...")
    print(f"Es waren noch {gamefield.n_current_food_fields} Futterfelder übrig.")
    e = input("Möchtest du es noch mal probieren? (j/n) ")
    if (e == "j"):
        restart()
    else:
        quit()
        
# called when PacMan has won the game
def won():
    print("Du hast gewonnen!")
    e = input("Möchtest du noch mal spielen? (j/n) ")
    if (e == "j"):
        restart()
    else:
        quit()
        
# resets everything and restarts the game from the beginning
def restart():
    global gamefield
    gamefield.load_from_file("Levels/Level1.txt")
    main()
                    
def main():
    gamefield.load_from_file("Levels/Level1.txt")

    while True:
        os.system('cls')
        gamefield.step()
        gamefield.print()
        for i in range(0,10):
            if msvcrt.kbhit():
                msvcrt.getch()
                key = msvcrt.getch()

                if key[0] == 72:
                    gamefield.user_input_direction = Direction.NORTH
                elif key[0] == 80:
                    gamefield.user_input_direction = Direction.SOUTH
                elif key[0] == 75:
                    gamefield.user_input_direction = Direction.WEST
                elif key[0] == 77:
                    gamefield.user_input_direction = Direction.EAST
                    
            time.sleep(speed/10.0)

main()

