class QualityScorer:
    def __init__(self):
        self.dimensions = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.20,
            'timeliness': 0.15,
            'validity': 0.15
        }
    
    def calculate_overall_score(self, dimension_scores):
        weighted_score = sum(
            score * weight 
            for score, weight in zip(dimension_scores.values(), self.dimensions.values())
        )
        return min(100, max(0, weighted_score))
