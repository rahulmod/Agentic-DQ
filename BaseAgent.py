class BaseAgent:
    def __init__(self, model_config, specialization):
        self.model = self.initialize_model(model_config)
        self.specialization = specialization
        self.context_window = model_config['context_limit']
    
    def process(self, data_chunk, context):
        prompt = self.build_specialized_prompt(data_chunk, context)
        response = self.model.generate(prompt)
        return self.parse_response(response)
    
    def build_specialized_prompt(self, data, context):
        # Agent-specific prompt engineering
        pass
