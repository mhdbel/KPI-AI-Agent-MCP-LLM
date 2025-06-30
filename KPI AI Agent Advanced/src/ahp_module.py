import ahpy
import openai
from src.config import load_secrets

secrets = load_secrets()
openai.api_key = secrets["OPENAI_API_KEY"]

class AHPAnalysis:
    def __init__(self, criteria_comparisons: dict):
        self.criteria = ahpy.Compare(
            name='Criteria',
            comparisons=criteria_comparisons,
            precision=3,
            random_index='saaty'
        )
        self._validate_consistency()
    
    def _validate_consistency(self):
        if self.criteria.consistency_ratio > 0.1:
            raise ValueError(f"CR: {self.criteria.consistency_ratio:.2f} exceeds 0.1")
    
    def get_explanation(self) -> str:
        prompt = f"Explain these AHP criteria weights:\n{self.criteria.report()}"
        return query_llm(prompt)
    
    def get_what_if(self, modified_weights: dict) -> dict:
        new_criteria = ahpy.Compare(
            name='Criteria',
            comparisons=modified_weights,
            precision=3,
            random_index='saaty'
        )
        return new_criteria.get_priority_vector()

def query_llm(prompt: str) -> str:
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"