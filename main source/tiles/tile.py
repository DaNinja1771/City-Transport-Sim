class Tile:
    def __init__(self, type):
        self.type = type
        self.occupied = []
    
    def setPerson(self, person):
        self.occupied.append(person)
    
    def removePerson(self, targetId):
        for i, agent in enumerate(self.occupied):
            if agent == targetId:
                del self.occupied[i]


    def check_occupancy(self):
        if(len(self.occupied) > 0):
            return True
        else:
            return False
        
    def getOccupants(self):
        return self.occupied
    
    def get_type(self):
        return self.type

    def set_type(self, typeIn):
        self.type = typeIn