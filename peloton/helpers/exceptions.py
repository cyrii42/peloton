class PelotonInstructorNotFoundError(Exception):
    pass

class WorkoutMismatchError(Exception):
    pass 

class NaiveDatetimeError(Exception):
    def __init__(self, dt, message="Input datetime object is not timezone-aware"):
        self.dt = dt
        self.message = message
        super().__init__(self.message)