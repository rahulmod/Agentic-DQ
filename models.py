# enterprise_dq/models.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class QualityMetrics:
    completeness: float
    accuracy: float
    consistency: float
    validity: float
    timeliness: float
    
    def calculate_overall_score(self) -> float:
        weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.20,
            'validity': 0.15,
            'timeliness': 0.15
        }
        
        return (
            self.completeness * weights['completeness'] +
            self.accuracy * weights['accuracy'] +
            self.consistency * weights['consistency'] +
            self.validity * weights['validity'] +
            self.timeliness * weights['timeliness']
        )

@dataclass
class QualityIssue:
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'completeness', 'accuracy', etc.
    description: str
    column: Optional[str]
    row_number: Optional[int]
    suggested_fix: Optional[str]

@dataclass
class QualityRule:
    column: str
    rule_type: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            'column': self.column,
            'rule_type': self.rule_type,
            'parameters': self.parameters
        }

@dataclass
class QualityResult:
    overall_score: float
    metrics: QualityMetrics
    issues: List[QualityIssue]
    processed_rows: int
    processing_time: float
    timestamp: datetime = datetime.now()

# enterprise_dq/exceptions.py
class DataQualityException(Exception):
    """Base exception for data quality operations"""
    pass

class APIException(DataQualityException):
    """Exception for API-related errors"""
    pass

class ValidationException(DataQualityException):
    """Exception for validation errors"""
    pass
