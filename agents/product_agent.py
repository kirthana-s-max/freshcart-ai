import pandas as pd
from pathlib import Path
from typing import List, Optional

class ProductAgent:
    def __init__(self, csv_path: str = "data/products.csv"):
        self.csv_path = Path(csv_path)
        self._products = None

    def _load_products(self) -> pd.DataFrame:
        if self._products is None:
            self._products = pd.read_csv(self.csv_path)
        return self._products

    def get_all_products(self) -> List[dict]:
        df = self._load_products()
        return df.to_dict('records')

    def get_products_by_category(self, category: str) -> List[dict]:
        df = self._load_products()
        filtered = df[df['category'].str.lower() == category.lower()]
        return filtered.to_dict('records')

    def search_products(self, keyword: str) -> List[dict]:
        df = self._load_products()
        keyword_lower = keyword.lower()
        filtered = df[
            df['name'].str.lower().str.contains(keyword_lower, na=False) |
            df['category'].str.lower().str.contains(keyword_lower, na=False) |
            df['description'].str.lower().str.contains(keyword_lower, na=False)
        ]
        return filtered.to_dict('records')

    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        df = self._load_products()
        product = df[df['id'] == product_id]
        if product.empty:
            return None
        return product.iloc[0].to_dict()

    def get_categories(self) -> List[str]:
        df = self._load_products()
        return df['category'].unique().tolist()
