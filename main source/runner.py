from agents.agent import Agent
from tiles.tile import Tile
import copy

class MainRunner:
    def __init__(self):

        self.cityGrid = []

        with open('map_10x10_hyperloop_ga.txt', 'r') as file:
            for line in file:
                tempRow = []
                for tile in line:
                    if (tile == 'R'):
                        tempRow.append(Tile("Road"))
                    if (tile == 'P'):
                        tempRow.append(Tile("Park"))
                    if (tile == 'H'):
                        tempRow.append(Tile("Hyperloop"))
                    if (tile == 'M'):
                        tempRow.append(Tile("Mall"))
                    if (tile == 'F'):
                        tempRow.append(Tile("Factory"))
                self.cityGrid.append(copy.deepcopy(tempRow))

        self.boardDimension = 10
        self.agentList =  [Agent(0,0,9,3,1,0), Agent(9,1,4,0,2,0), Agent(0,9,7,0,3,0), Agent(2,3,9,9,4,1), Agent(9,0,1,9,5,0)]
        self.agentMap = {}
        for i,agent in enumerate(self.agentList):
            self.agentMap[agent.getAgentId()] = self.agentList[i]

        # for 10x10: (3,3), (7,8), (9,1)
        #  [Agent(0,0,9,3,1,1), Agent(9,1,4,0,2,0), Agent(0,9,7,0,3,0), Agent(2,3,9,9,4,0), Agent(9,0,1,9,5,0)]
        # for 25x25: [(13,0), (10,7), (11,24)]
        # [Agent(0,1,13,20,1,0), Agent(1,5,22,20,2,0), Agent(23,23,17,4,4,0), Agent(23,1,5,16,5,0), Agent(15,7,2,23,6,0), Agent(7,9,1,19,7,0), Agent(14,19,5,1,8,0), Agent(23,14,3,5,9,0), Agent(11,14,22,23,10,0), Agent(1,1,9,9,3,0)]
        # for 100x100: [(0,1), (59,4), (74,82)]
        # [Agent(0,1,74,82,1,1), Agent(92,6,16,87,2,0), Agent(30,38,90,60,3,0), Agent(44,0,55,78,4,1), Agent(79,36,5,65,5,0), Agent(59,51,90,70,6,0), Agent(68,26,42,79,7,1), Agent(53,63,0,29,8,0), Agent(23,88,56,1,9,0), Agent(93,95,22,56,10,1), Agent(87,44,30,24,11,0), Agent(42,45,0,0,12,0), Agent(64,77,64,17,13,1), Agent(17,31,68,44,14,0), Agent(86,17,22,87,15,0), Agent(90,59,22,4,16,0), Agent(12,99,56,18,17,0), Agent(79,21,0,90,18,0), Agent(90,71,18,31,19,0), Agent(64,56,31,18,20,1), Agent(56,6,24,87,21,0), Agent(8,13,50,31,22,0), Agent(22,44,80,51,23,1), Agent(43,25,67,91,24,0), Agent(12,82,80,61,25,0)]
        self.hyperLoops = [(6,0), (9,0), (0,9)] # Manually adjust hyperloop locations as needed
        
    def buildGridMaps(self):
        self.cityGridMap = {0: copy.deepcopy(self.cityGrid)}
        # Build additional city grid maps for extended simulation runs
        # also manually have to change the range for bigger boards here
        for i in range(1, 15):
            self.cityGridMap[i] = copy.deepcopy(self.cityGridMap[0])


    def runTraversal(self):
        for agent in self.agentList:
            agent.make_path(self.cityGridMap, self.boardDimension, self.hyperLoops)
        # self.printResults()

    def printResults(self):
        for i, map in enumerate(self.cityGridMap.values()):
            printList = []
            for r in map:
                tempR = []
                for c in r:
                    letters = c.get_type()[0]
                    if c.check_occupancy():
                        for occupant in c.getOccupants():
                            letters += str(occupant)
                            letters += self.agentMap[occupant].getAgentType()[0]
                    tempR.append(letters)
                printList.append(tempR)
            print(f"City on iteration {i}")
            for r in printList:
                print(r)

        cumCost = 0
        for agent in self.agentList:
            cumCost += agent.cost
        print(f"The average cost per agent is {cumCost / len(self.agentList)}")

    def printResultsToTextFile(self):
        with open('results.txt', 'w') as file:
            for i, map in enumerate(self.cityGridMap.values()):
                printList = []
                for r in map:
                    tempR = []
                    for c in r:
                        letters = c.get_type()[0]
                        if c.check_occupancy():
                            for occupant in c.getOccupants():
                                letters += str(occupant)
                                letters += self.agentMap[occupant].getAgentType()[0]
                        tempR.append(letters)
                    # Only append the row if it contains non-empty data
                    if any(tempR):  # This checks if any cells in the row are non-empty
                        printList.append(tempR)
                # Write to file only if printList is not empty
                if printList:
                    file.write(str(printList))
                    file.write("\n")




    def getCumCost(self):
        cumCost = 0
        for agent in self.agentList:
            cumCost += agent.cost
        return cumCost
# To run the traversal and analysis for the current map setup:
if __name__ == "__main__":
    runner = MainRunner()
    runner.buildGridMaps()
    runner.runTraversal()
    runner.printResults()
    runner.printResultsToTextFile()
