def smart_chunking(dataset, model_context_limit):
    chunks = []
    current_chunk = []
    token_count = 0
    
    for record in dataset:
        record_tokens = estimate_tokens(record)
        if token_count + record_tokens > model_context_limit * 0.8:
            chunks.append(current_chunk)
            current_chunk = [record]
            token_count = record_tokens
        else:
            current_chunk.append(record)
            token_count += record_tokens
    
    return chunks
