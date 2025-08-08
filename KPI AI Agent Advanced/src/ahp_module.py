import ahpy
from src.config import query_llm

class AHPAnalysis:
    def __init__(self, criteria_comparisons: dict):
        """
        Initialize AHP analysis with pairwise comparisons.
        
        Args:
            criteria_comparisons (dict): Pairwise comparison matrix as a dictionary.
        """
        if not isinstance(criteria_comparisons, dict) or not criteria_comparisons:
            raise ValueError("criteria_comparisons must be a non-empty dictionary.")
        
        self.criteria = ahpy.Compare(
            name='Criteria',
            comparisons=criteria_comparisons,
            precision=3,
            random_index='saaty'
        )
        self._validate_consistency()
    
    def _validate_consistency(self):
        cr = self.criteria.consistency_ratio
        logging.info(f"Consistency Ratio (CR): {cr:.2f}")
        if cr > 0.1:
            raise ValueError(
                f"Consistency Ratio (CR): {cr:.2f} exceeds 0.1. "
                "Please revise your pairwise comparisons to improve consistency."
            )
    
    def get_explanation(self) -> str:
        """
        Generate an LLM-based explanation of the AHP criteria weights.
        
        Returns:
            str: LLM-generated explanation.
        """
        report = self.criteria.report()
        prompt = (
            f"Explain the following Analytic Hierarchy Process (AHP) criteria weights:\n"
            f"{report}\n"
            "Provide clear reasoning and highlight any key insights."
        )
        return query_llm(prompt)
    
    def get_what_if(self, modified_weights: dict) -> dict:
        """
        Simulate a "what-if" scenario with modified weights.
        
        Args:
            modified_weights (dict): Modified pairwise comparison matrix.
        
        Returns:
            dict: Updated priority vector.
        """
        if not isinstance(modified_weights, dict) or not modified_weights:
            raise ValueError("modified_weights must be a non-empty dictionary.")
        
        new_criteria = ahpy.Compare(
            name='Criteria',
            comparisons=modified_weights,
            precision=3,
            random_index='saaty'
        )
        return new_criteria.get_priority_vector()
