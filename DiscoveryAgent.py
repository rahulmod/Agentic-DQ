class DiscoveryAgent(BaseAgent):
    def discover_schema(self, dataset):
        chunks = self.chunk_data(dataset)
        discoveries = []
        
        for chunk in chunks:
            prompt = f"""
            Analyze this data sample:
            {chunk}
            
            Provide:
            1. Column analysis (type, nullability, patterns)
            2. Potential relationships
            3. Business meaning inference
            4. Data quality concerns
            
            Format as structured JSON.
            """
            discoveries.append(self.model.generate(prompt))
        
        return self.merge_discoveries(discoveries)
