class tester:
    
    def __init__(self):
        self.numbers = [{"number":4088870718, "provider":'tmomail.net'}]
        
    def iterate(self):
        for user in self.numbers:
            print user["number"]
            
if (__name__ == "__main__"):
    e = tester()
    e.iterate()