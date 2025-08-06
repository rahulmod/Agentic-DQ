class CostOptimizedRouter:
    def route_task(self, task_type, complexity, budget):
        model_costs = {
            'gemini_flash': 0.075,
            'gpt4_mini': 0.15,
            'claude_haiku': 0.25
        }
        
        if complexity == 'low' and budget == 'tight':
            return 'gemini_flash'
        elif complexity == 'medium':
            return 'gpt4_mini'
        else:
            return 'claude_haiku'
