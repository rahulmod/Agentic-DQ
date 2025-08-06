# enterprise_dq/client.py
import asyncio
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
import aiohttp
import json
from datetime import datetime
import hashlib

class DataQualityClient:
    def __init__(self, 
                 api_endpoint: str,
                 api_key: str,
                 batch_size: int = 1000,
                 max_workers: int = 5):
        self.api_endpoint = api_endpoint.rstrip('/')
        self.api_key = api_key
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def assess_dataframe_quality(self, 
                                df: pd.DataFrame,
                                rules: Optional[List[QualityRule]] = None,
                                profile_data: bool = True) -> QualityResult:
        """
        Synchronous wrapper for bulk data quality assessment
        """
        return asyncio.run(self.assess_dataframe_quality_async(df, rules, profile_data))
    
    async def assess_dataframe_quality_async(self, 
                                           df: pd.DataFrame,
                                           rules: Optional[List[QualityRule]] = None,
                                           profile_data: bool = True) -> QualityResult:
        """
        Perform comprehensive data quality assessment on pandas DataFrame
        """
        if self.session is None:
            raise DataQualityException("Client not initialized. Use async context manager.")
        
        # Split dataframe into batches
        batches = self._split_dataframe(df, self.batch_size)
        
        # Process batches concurrently
        semaphore = asyncio.Semaphore(self.max_workers)
        tasks = [
            self._process_batch(batch, idx, rules, profile_data, semaphore)
            for idx, batch in enumerate(batches)
        ]
        
        batch_results = await asyncio.gather(*tasks)
        
        # Aggregate results
        return self._aggregate_results(batch_results, df.shape[0])
    
    async def _process_batch(self, 
                           batch: pd.DataFrame,
                           batch_id: int,
                           rules: Optional[List[QualityRule]],
                           profile_data: bool,
                           semaphore: asyncio.Semaphore) -> Dict:
        """
        Process a single batch of data
        """
        async with semaphore:
            # Convert batch to JSON
            batch_data = {
                'batch_id': batch_id,
                'data': batch.to_dict('records'),
                'schema': self._extract_schema(batch),
                'rules': [rule.to_dict() for rule in (rules or [])],
                'profile_data': profile_data
            }
            
            # Send to API
            async with self.session.post(
                f"{self.api_endpoint}/api/v1/quality/assess/batch",
                json=batch_data
            ) as response:
                if response.status != 200:
                    raise DataQualityException(f"API error: {response.status}")
                
                return await response.json()
    
    def _split_dataframe(self, df: pd.DataFrame, batch_size: int) -> List[pd.DataFrame]:
        """
        Split DataFrame into smaller batches
        """
        return [df[i:i + batch_size] for i in range(0, len(df), batch_size)]
    
    def _extract_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Extract schema information from DataFrame
        """
        return {
            col: str(dtype) for col, dtype in df.dtypes.items()
        }
    
    def _aggregate_results(self, batch_results: List[Dict], total_rows: int) -> QualityResult:
        """
        Aggregate results from multiple batches
        """
        # Combine quality scores
        total_completeness = sum(r['metrics']['completeness'] * r['row_count'] for r in batch_results)
        total_accuracy = sum(r['metrics']['accuracy'] * r['row_count'] for r in batch_results)
        total_consistency = sum(r['metrics']['consistency'] * r['row_count'] for r in batch_results)
        total_validity = sum(r['metrics']['validity'] * r['row_count'] for r in batch_results)
        total_timeliness = sum(r['metrics']['timeliness'] * r['row_count'] for r in batch_results)
        
        # Calculate weighted averages
        metrics = QualityMetrics(
            completeness=total_completeness / total_rows,
            accuracy=total_accuracy / total_rows,
            consistency=total_consistency / total_rows,
            validity=total_validity / total_rows,
            timeliness=total_timeliness / total_rows
        )
        
        # Combine issues
        all_issues = []
        for result in batch_results:
            all_issues.extend(result.get('issues', []))
        
        return QualityResult(
            overall_score=metrics.calculate_overall_score(),
            metrics=metrics,
            issues=all_issues,
            processed_rows=total_rows,
            processing_time=sum(r['processing_time'] for r in batch_results)
        )

# Usage Example
async def main():
    async with DataQualityClient(
        api_endpoint="https://api.yourdomain.com",
        api_key="your-api-key"
    ) as client:
        
        # Load your data
        df = pd.read_csv("large_dataset.csv")
        
        # Define quality rules
        rules = [
            QualityRule("email", "email_format", {"pattern": r"^[^@]+@[^@]+\.[^@]+$"}),
            QualityRule("age", "range", {"min": 0, "max": 150}),
            QualityRule("phone", "not_null"),
        ]
        
        # Assess quality
        result = await client.assess_dataframe_quality_async(df, rules)
        
        print(f"Overall Quality Score: {result.overall_score:.2f}")
        print(f"Issues Found: {len(result.issues)}")
