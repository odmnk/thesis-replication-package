class BackNForthIterator(object):

    ABOVE = 0
    BELOW = 1

    def __init__(self, list_):
        self.list = list_
        middle_of_list = len(self.list)//2
        self.above = middle_of_list
        self.below = middle_of_list

        self.previous_iteration = None 
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.previous_iteration == None:
            self.previous_iteration = BackNForthIterator.BELOW
            index = self.below
        elif self.previous_iteration == BackNForthIterator.BELOW:
            # Return item from above 
            # Prevent accessing the list in reverse.
            if not self.above > 0:
                raise StopIteration
            self.above -= 1
            self.previous_iteration = BackNForthIterator.ABOVE
            index = self.above
        else:
            # Return item from below
            self.below += 1
            self.previous_iteration = BackNForthIterator.BELOW
            index = self.below

        try:
            return self.list[index]
        except IndexError:
           raise StopIteration  # Done iterating.
