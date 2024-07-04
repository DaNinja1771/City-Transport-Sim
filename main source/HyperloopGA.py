import random
import numpy as np
from runner import MainRunner
import time

# A genetic algorithm crossed with

class HyperloopGA:
    def __init__(self, population_size, num_hyperloops, mutation_rate=0.1, crossover_rate=0.7, grid_size=10):
        self.population_size = population_size
        self.num_hyperloops = num_hyperloops
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.grid_size = grid_size
        self.population = self.initialize_population()

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            # Randomly choose 'num_hyperloops' different (x, y) locations in the grid
            hyperloops = set()
            while len(hyperloops) < self.num_hyperloops:
                x = random.randint(0, self.grid_size - 1)
                y = random.randint(0, self.grid_size - 1)
                hyperloops.add((x, y))
            population.append(list(hyperloops))
        return population

    def fitness(self, individual):
        runner = MainRunner()
        runner.hyperLoops = individual
        for x, y in individual:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                runner.cityGrid[x][y].type = "Hyperloop"
        runner.buildGridMaps()
        runner.runTraversal()
        return -runner.getCumCost()

    def hill_climb(self, individual):
        print('climbing')
        for _ in range(1):
            candidate = individual[:]
            index = random.randint(0, len(candidate) - 1)
            new_pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            candidate[index] = new_pos
            if self.fitness(candidate) > self.fitness(individual):
                individual = candidate
        return individual

    def mutate_and_improve(self, individual):
        if random.random() < self.mutation_rate:
            mutation_point = random.randint(0, self.num_hyperloops - 1)
            new_x = random.randint(0, self.grid_size - 1)
            new_y = random.randint(0, self.grid_size - 1)
            individual[mutation_point] = (new_x, new_y)
        return self.hill_climb(individual)

    def select_parent(self):
        tournament_size = 3
        contenders = random.sample(self.population, tournament_size)
        best = max(contenders, key=self.fitness)
        return best

    def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.num_hyperloops - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return [child1, child2]
        return [parent1, parent2]

    def run_generation(self):
        new_population = []
        while len(new_population) < self.population_size:
            parent1 = self.select_parent()
            parent2 = self.select_parent()
            for child in self.crossover(parent1, parent2):
                improved_child = self.mutate_and_improve(child)
                new_population.append(improved_child)
        self.population = new_population[:self.population_size]

    def run(self, generations):
        best_individual = None
        best_fitness = float('-inf')
        for gen in range(generations):
            self.run_generation()
            current_best = max(self.population, key=self.fitness)
            current_best_fitness = self.fitness(current_best)
            print(f"Generation {gen+1}")
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = current_best
                print(f"Generation {gen+1}: New best configuration found with fitness {best_fitness}")
                print(f"Hyperloop locations: {best_individual}")
        return best_individual

# Run genetic algorithm
def main():
    start_time = time.time()
    ga = HyperloopGA(population_size=50, num_hyperloops=3, grid_size=25)
    best_solution = ga.run(25)
    end_time = time.time()
    print("Best hyperloop placement:", best_solution)
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    main()
