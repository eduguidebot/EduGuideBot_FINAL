import os
import json
import logging
from typing import Dict, List, Any, Optional
import secrets

from src.core.data_loader import UniversityDataManager
from src.core.recommender import UniversityRecommender

logger = logging.getLogger(__name__)

class ResultGenerator:
    """Generates recommendation results and saves them for web display"""
    
    def __init__(self, data_path: str, results_dir: str = "static/data"):
        self.data_manager = UniversityDataManager(data_path)
        self.recommender = UniversityRecommender(self.data_manager)
        self.results_dir = results_dir
        
        # Ensure the results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
    
    def generate_results(self, user_profile: Dict[str, Any], user_id: Optional[int] = None) -> Optional[str]:
        """
        Generate recommendation results for a user profile and save them to a JSON file
        Returns the result ID that can be used to access the results, or None if there was an error
        """
        # Generate a unique ID for this result if not provided
        result_id = str(user_id) if user_id else secrets.token_urlsafe(8)
        
        # Get recommendations from the recommender
        recommendations = self.recommender.recommend(user_profile, top_n=5)
        
        # Create result data including the user profile and recommendations
        result_data = {
            "user_profile": user_profile,
            "recommendations": recommendations,
            "result_id": result_id,
            "timestamp": None  # This would be set to the current time in a real implementation
        }
        
        # Save the result data to a JSON file
        result_file = os.path.join(self.results_dir, f"result_{result_id}.json")
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {result_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return None
        
        return result_id
    
    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve recommendation results by ID, or None if not found"""
        result_file = os.path.join(self.results_dir, f"result_{result_id}.json")
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Result file not found: {result_file}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {result_file}")
            return None 