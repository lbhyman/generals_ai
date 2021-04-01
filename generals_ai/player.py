

class Player:
    
    def __init__(self, name, stars=0):
        self.name = name
        self.army = 1
        self.land = 1
        self.generals = 1
        self.stars = stars
        self.alive = True
        self.afk = False
        
    def set_army(self, value):
        self.army = value
    
    def set_land(self, value):
        self.land = value
        
    def increment_generals(self, value):
        self.generals += value
        if self.generals <= 0:
            self.die()
        
    def die(self):
        self.alive = False
        self.generals = 0
    
    