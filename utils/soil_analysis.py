class SoilAnalyzer:
    """Soil analysis and recommendations"""
    
    def __init__(self):
        self.soil_types = {
            'Alluvial': {
                'suitable_crops': ['Rice', 'Wheat', 'Sugarcane', 'Cotton', 'Maize'],
                'characteristics': 'Rich in nutrients, good water retention',
                'ph_range': '6.5-7.5'
            },
            'Black': {
                'suitable_crops': ['Cotton', 'Soybean', 'Wheat', 'Jowar', 'Sunflower'],
                'characteristics': 'High clay content, excellent moisture retention',
                'ph_range': '7.0-8.5'
            },
            'Red': {
                'suitable_crops': ['Groundnut', 'Pulses', 'Millets', 'Cotton'],
                'characteristics': 'Well-drained, low fertility',
                'ph_range': '5.5-7.0'
            },
            'Laterite': {
                'suitable_crops': ['Cashew', 'Coconut', 'Tea', 'Coffee'],
                'characteristics': 'High iron content, acidic',
                'ph_range': '5.0-6.5'
            },
            'Sandy': {
                'suitable_crops': ['Groundnut', 'Watermelon', 'Muskmelon', 'Pulses'],
                'characteristics': 'Good drainage, low water retention',
                'ph_range': '6.0-7.0'
            },
            'Clay': {
                'suitable_crops': ['Rice', 'Wheat', 'Sugarcane'],
                'characteristics': 'Poor drainage, high water retention',
                'ph_range': '6.5-7.5'
            }
        }
    
    def get_soil_recommendations(self, soil_type):
        """Get recommendations for a soil type"""
        if soil_type in self.soil_types:
            return {
                'success': True,
                'soil_type': soil_type,
                'data': self.soil_types[soil_type]
            }
        
        return {
            'success': False,
            'error': 'Soil type not found'
        }
    
    def recommend_crops_by_soil(self, soil_type):
        """Recommend crops based on soil type"""
        if soil_type in self.soil_types:
            return self.soil_types[soil_type]['suitable_crops']
        return []
    
    def get_soil_improvement_tips(self, soil_type):
        """Get soil improvement recommendations"""
        tips = {
            'Alluvial': [
                'Add organic matter to maintain fertility',
                'Practice crop rotation',
                'Use green manure crops'
            ],
            'Black': [
                'Ensure proper drainage during monsoon',
                'Add gypsum to improve structure',
                'Use deep-rooted crops to break hardpan'
            ],
            'Red': [
                'Add lime to reduce acidity',
                'Use organic fertilizers regularly',
                'Practice mulching to retain moisture'
            ],
            'Laterite': [
                'Add lime to neutralize acidity',
                'Use phosphate fertilizers',
                'Incorporate organic matter'
            ],
            'Sandy': [
                'Add organic matter to improve water retention',
                'Use drip irrigation',
                'Apply mulch to reduce evaporation'
            ],
            'Clay': [
                'Improve drainage with organic matter',
                'Avoid working soil when wet',
                'Use raised beds for better drainage'
            ]
        }
        
        return tips.get(soil_type, [])
if __name__ == "__main__":
    analyzer = SoilAnalyzer()
    print(analyzer.get_soil_recommendations("Alluvial"))
    print(analyzer.recommend_crops_by_soil("Alluvial"))

