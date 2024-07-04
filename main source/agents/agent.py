import heapq
import copy
from concurrent.futures import ProcessPoolExecutor

class Agent:
    def __init__(self, startRow = 0, startCol = 0, endRow = 0, endCol = 0, agentId = 0, disabiility = 0):
        self.start = (startRow, startCol)
        self.end = (endRow, endCol)
        self.agentType = "unknown"
        self.agentId = agentId
        self.cost = 0
        self.disability = disabiility


    def getAgentId(self):
        return self.agentId
    
    def getAgentType(self):
        return self.agentType
    
    def getDisabilityStatus(self):
        # 1 if disabled, 0 if not
        return self.disability


    # This returns a list of valid moves so the traversal algorithm knows what choices it can make at each position.
    def get_valid_moves_pedestrian(self, cityGridMap, currentCycle, dimension, currPos, hyperLoops):
        # Pedestrians are allowed to use the hyperloop.
        # The cityGridMap maps the cycleCount:mapOfObjects. The map of objects is comprised of tiles, 
        # each tracking the number of agent occupants or the current state of the city at that cycle count.
        # The current cycle is the cycle we're on, and dimension is the dimensions of the city we're working with.
        ROW, COL = dimension, dimension  # Set dimensions for rows and columns

        # Access the cityGridMap at the currentCycle count
        currentCityMap = cityGridMap[currentCycle]

        # Initialize list to track what tiles/moves are valid destinations
        validDestinations = []

        currRow, currCol = currPos  # Current position of the pedestrian

        # Helper function to check valid move
        def is_valid_move(row, col):
            if 0 <= row < ROW and 0 <= col < COL:
                tile = currentCityMap[row][col]
                return not tile.check_occupancy() and tile.get_type() != "Factory"
            return False

        # Check movement in all four directions
        if is_valid_move(currRow - 1, currCol):  # Up
            validDestinations.append((currRow - 1, currCol))
        if is_valid_move(currRow + 1, currCol):  # Down
            validDestinations.append((currRow + 1, currCol))
        if is_valid_move(currRow, currCol - 1):  # Left
            validDestinations.append((currRow, currCol - 1))
        if is_valid_move(currRow, currCol + 1):  # Right
            validDestinations.append((currRow, currCol + 1))

        # Add the option to stay in the current position (waiting option)
        validDestinations.append((currRow, currCol))

        # If the current tile is a hyperloop, add the possible hyperloop positions:
        # we don't do an occupancy check here since hyperloop stations have infinite occupancy
        if (currentCityMap[currRow][currCol].get_type() == "Hyperloop"):
            validDestinations.extend(hyperLoops)  # Extend the list with the contents of hyperLoops

        return validDestinations


    
    def get_valid_moves_car(self, cityGridMap, currentCycle, dimension, currPos, hyperLoops):
        ROW, COL = dimension, dimension
        currentCityMap = cityGridMap[currentCycle]
        validDestinations = []
        currRow, currCol = currPos

        # Define a helper function to check if a position is within the grid and the tile is a road and not occupied
        def is_valid_move(row, col):
            if 0 <= row < ROW and 0 <= col < COL:
                tile = currentCityMap[row][col]
                return tile.get_type() == "Road" and not tile.check_occupancy()
            return False

        # Function to check contiguous road for a given step size and direction
        def check_contiguous_direction(start, end, fixed, is_row_fixed):
            path = []
            if is_row_fixed:  # Movement in column direction
                step = 1 if end > start else -1
                for col in range(start, end + step, step):
                    if is_valid_move(fixed, col):
                        path.append((fixed, col))
                    else:
                        break  # Stop if a non-road or occupied tile is encountered
            else:  # Movement in row direction
                step = 1 if end > start else -1
                for row in range(start, end + step, step):
                    if is_valid_move(row, fixed):
                        path.append((row, fixed))
                    else:
                        break  # Stop if a non-road or occupied tile is encountered
            return path

        # Check moves in each direction up to 3 tiles away
        # Movement in rows (up and down)
        validDestinations.extend(check_contiguous_direction(currRow - 1, currRow - 3, currCol, False))
        validDestinations.extend(check_contiguous_direction(currRow + 1, currRow + 3, currCol, False))

        # Movement in columns (left and right)
        validDestinations.extend(check_contiguous_direction(currCol - 1, currCol - 3, currRow, True))
        validDestinations.extend(check_contiguous_direction(currCol + 1, currCol + 3, currRow, True))

        # Add the waiting option to stay in the same position
        validDestinations.append((currRow, currCol))

        return validDestinations
    def get_valid_moves_biker(self, cityGridMap, currentCycle, dimension, currPos, hyperLoops):
        ROW, COL = dimension, dimension
        currentCityMap = cityGridMap[currentCycle]
        validDestinations = []
        currRow, currCol = currPos

        # Define a helper function to check if a position is within the grid and the tile is not a park, not a factory, and not occupied
        def is_valid_move(row, col):
            if 0 <= row < ROW and 0 <= col < COL:
                tile = currentCityMap[row][col]
                return tile.get_type() not in ["Factory"] and not tile.check_occupancy() and tile.get_type() not in ["Mall"]
            return False

        # Function to check contiguous paths, allowing bikers to move through tiles unless blocked by a park or factory
        def check_contiguous_direction(start, end, fixed, is_row_fixed):
            path = []
            if is_row_fixed:  # Movement in column direction
                step = 1 if end > start else -1
                for col in range(start, end + step, step):
                    if is_valid_move(fixed, col):
                        path.append((fixed, col))
                    else:
                        break  # Stop if a park or factory or occupied tile is encountered
            else:  # Movement in row direction
                step = 1 if end > start else -1
                for row in range(start, end + step, step):
                    if is_valid_move(row, fixed):
                        path.append((row, fixed))
                    else:
                        break  # Stop if a park or factory or occupied tile is encountered
            return path

        # Check moves in each direction up to 2 tiles away
        # Movement in rows (up and down)
        validDestinations.extend(check_contiguous_direction(currRow - 1, currRow - 2, currCol, False))
        validDestinations.extend(check_contiguous_direction(currRow + 1, currRow + 2, currCol, False))

        # Movement in columns (left and right)
        validDestinations.extend(check_contiguous_direction(currCol - 1, currCol - 2, currRow, True))
        validDestinations.extend(check_contiguous_direction(currCol + 1, currCol + 2, currRow, True))

        # Add the waiting option to stay in the same position
        validDestinations.append((currRow, currCol))

        return validDestinations

    def heuristic(self, a, b):
        """Calculate the Manhattan distance between two points"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
               
    def astar(self, grid, dimension, obstacleFunction, hyperLoops):
        open_list = []
        came_from = {}  # To track the path
        g_score = {self.start: 0}
        f_score = {self.start: self.heuristic(self.start, self.end)}

        # Add the start position to the open list
        heapq.heappush(open_list, (f_score[self.start], self.start))

        while open_list:
            # Get the current position
            current = heapq.heappop(open_list)[1]

            # If it's the goal, reconstruct the path
            if current == self.end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                return path[::-1]

            # See if the next city exists at this depth, if it doesn't make a copy of the city before and add it in. Note, this is a copy the city grid map, we have to add the real moves into the 'real' map later
            if  g_score[current]+1 not in grid:
                grid[g_score[current]+1] = copy.deepcopy(grid[g_score[current]])

            # Generate possible moves
            valid_moves = obstacleFunction(grid, g_score[current] + 1, dimension, current, hyperLoops)

            for neighbor in valid_moves:
                # Calculate tentative g score for neighbor
                tentative_g_score = g_score[current] + 1  # Assuming each move has a cost of 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, self.end)
                    if (f_score[neighbor], neighbor) not in open_list:
                        heapq.heappush(open_list, (f_score[neighbor], neighbor))
        return None  # If no path is found

    def add_to_open(open_list, f_score, neighbor):
        for score, pos in open_list:
            if pos == neighbor and f_score[neighbor] > score:
                return False
        return True

    def make_path(self, cityGridMap, boardDimension, hyperLoops):    
        # if self.disability:
        #     future_car = self.astar(copy.deepcopy(cityGridMap), boardDimension, self.get_valid_moves_car, hyperLoops)
        #     best_path_length = future_car
        #     best_type = "Car"

        #     # Mutate the city grid map to reflect our new calculated path
        #     for i, pos in enumerate(best_path_length):
        #         x, y = pos
        #         if i == 0:
        #             cityGridMap[i][x][y].setPerson(self.agentId)  # Set agent at the start position
        #         else:
        #             cityGridMap[i-1][x][y].removePerson(self.agentId)  # Remove agent from the previous tile
        #             cityGridMap[i][x][y].setPerson(self.agentId)  # Set agent at the new tile

        #     return

        # else:
            with ProcessPoolExecutor(max_workers=3) as executor:
                # Asynchronously execute each traversal
                future_pedestrian = executor.submit(self.astar, copy.deepcopy(cityGridMap), boardDimension, self.get_valid_moves_pedestrian, hyperLoops)
                future_biker = executor.submit(self.astar, copy.deepcopy(cityGridMap), boardDimension, self.get_valid_moves_biker, hyperLoops)
                future_car = executor.submit(self.astar, copy.deepcopy(cityGridMap), boardDimension, self.get_valid_moves_car, hyperLoops)

                # Collect results
                path_pedestrian = future_pedestrian.result()
                path_biker = future_biker.result()
                path_car = future_car.result()

            # Determine the best path among the three options
            results = [
                (path_pedestrian, "Pedestrian"),
                (path_biker, "Biker"),
                (path_car, "Car")
            ]
            # Filter out any None results (if no path found) and calculate path lengths
            valid_results = [(len(path), agent_type) for path, agent_type in results if path is not None]

            if not valid_results:
                print(f"No valid paths found for any mode of traversal for agent id {self.agentId}")
                return

            # Find the minimum result based on path length
            min_result = min(valid_results, key=lambda x: x[0])
            best_path_length, best_type = min_result

            # Update agent information based on the best result
            self.agentType = best_type
            self.cost = best_path_length - 1  # Subtract 1 as path includes the starting tile

            # Retrieve the best path from the results
            best_path = next(path for path, agent_type in results if agent_type == best_type)

            # Mutate the city grid map to reflect our new calculated path
            for i, pos in enumerate(best_path):
                x, y = pos
                if i == 0:
                    cityGridMap[i][x][y].setPerson(self.agentId)  # Set agent at the start position
                else:
                    cityGridMap[i-1][x][y].removePerson(self.agentId)  # Remove agent from the previous tile
                    cityGridMap[i][x][y].setPerson(self.agentId)  # Set agent at the new tile
