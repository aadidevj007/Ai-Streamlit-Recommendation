import pandas as pd
import numpy as np
from collections import defaultdict
class SimpleHybridRecommender:
    def __init__(self, products_df: pd.DataFrame, history_df: pd.DataFrame):
        self.products = products_df.copy()
        self.history = history_df.copy()
    def recommend(self, user_id:int, top_k:int=10):
        return self.products.head(top_k)
    def simulate_session(self, user_id:int, recs_df, steps:int=5):
        events=[]
        for i in range(min(steps, len(recs_df))):
            prod = recs_df.iloc[i]
            events.append({'step':i+1,'action':'viewed','product_id':int(prod['product_id']),'name':prod['name'],'price':float(prod['price']),'category':prod['category']})
        return pd.DataFrame(events)
