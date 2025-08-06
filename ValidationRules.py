class ValidationRules:
    def __init__(self):
        self.rules = {
            'completeness': self.check_completeness,
            'accuracy': self.check_accuracy,
            'consistency': self.check_consistency,
            'timeliness': self.check_timeliness,
            'validity': self.check_validity
        }
