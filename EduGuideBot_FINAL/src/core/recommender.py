from src.core.data_loader import UniversityDataManager

SPECIALIST_UNIVERSITIES = {
    'វិស្វកម្ម': [10, 27],
    'បច្ចេកវិទ្យា': [10, 27],
    'វេជ្ជសាស្ត្រ': [14, 15],
    'សុខភាព': [14, 15],
    'ច្បាប់': [12],
    'ធុរកិច្ច': [16, 35]
}

class UniversityRecommender:
    def __init__(self, data_manager: UniversityDataManager):
        self.data_manager = data_manager
        self.all_universities = self.data_manager.get_all_universities()

    def recommend(self, user_profile: dict, top_n: int = 3) -> list:
        candidates = self._hard_filter(user_profile)
        scored_results = self._calculate_scores(candidates, user_profile)
        return sorted(scored_results, key=lambda x: x['total_score'], reverse=True)[:top_n]

    def _hard_filter(self, user_profile: dict) -> list:
        candidate_universities = self.all_universities
        if user_profile.get('location') and user_profile['location'] != 'Any':
            candidate_universities = [u for u in candidate_universities if u.get('location') == user_profile['location']]
        if user_profile.get('max_budget'):
            candidate_universities = [u for u in candidate_universities if u['tuition_fees']['range_min'] <= user_profile['max_budget']]
        return candidate_universities

    def _calculate_scores(self, candidate_universities: list, user_profile: dict) -> list:
        scored_unis = []
        for uni in candidate_universities:
            score = 0
            # Score logic here...
            # Major Field Score
            major_count = sum(1 for f in uni.get('faculties', []) for m in f.get('majors', []) if m.get('category_km') == user_profile['core_field'])
            score += min(major_count * 5, 30)
            # Career Goal Score
            career_map = {'វិស្វករ': 'វិស្វកម្ម', 'អ្នកគ្រប់គ្រង': 'ធុរកិច្ច', 'វេជ្ជបណ្ឌិត': 'វេជ្ជសាស្ត្រ', 'គ្រូបង្រៀន': 'អប់រំ', 'អ្នកកฎหមាយ': 'ច្បាប់'}
            mapped_field = career_map.get(user_profile['career_goal'])
            if mapped_field and any(m.get('category_km') == mapped_field for f in uni.get('faculties', []) for m in f.get('majors', [])):
                score += 25
            # Budget Fit Score
            buffer = user_profile['max_budget'] - uni['tuition_fees']['range_max']
            if buffer > 500: score += 20
            elif buffer > 0: score += 10
            # English Strength Score
            if user_profile['english_proficiency'] >= 8 and uni['id'] in [4, 28, 36, 32]:
                score += 15
            # Specialization Score
            if uni['id'] in SPECIALIST_UNIVERSITIES.get(user_profile['core_field'], []):
                score += 20
            
            scored_unis.append({'university': uni, 'total_score': score})
        return scored_unis 