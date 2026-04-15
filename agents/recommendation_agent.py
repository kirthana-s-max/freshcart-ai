from typing import List, Dict
import random

class RecommendationAgent:
    def __init__(self, product_agent):
        self.product_agent = product_agent

    def recommend_by_product(self, product_id: int) -> List[Dict]:
        product = self.product_agent.get_product_by_id(product_id)
        if not product:
            return []
        
        return self.recommend_by_category(product['category'])

    def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        products = self.product_agent.get_products_by_category(category)
        if len(products) <= limit:
            return products
        
        recommended = random.sample(products, limit)
        return recommended

    def get_popular_products(self, limit: int = 10) -> List[Dict]:
        all_products = self.product_agent.get_all_products()
        if len(all_products) <= limit:
            return all_products
        return random.sample(all_products, limit)

    def get_complementary_products(self, product_id: int) -> List[Dict]:
        product = self.product_agent.get_product_by_id(product_id)
        if not product:
            return []
        
        category = product['category']
        complementary = {
            'vegetables': 'fruits',
            'fruits': 'nuts',
            'nuts': 'vegetables'
        }
        related_category = complementary.get(category, 'vegetables')
        return self.recommend_by_category(related_category, limit=3)

recommendation_agent = None

def init_recommendation_agent(product_agent):
    global recommendation_agent
    recommendation_agent = RecommendationAgent(product_agent)
    return recommendation_agent
