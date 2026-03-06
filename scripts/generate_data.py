# scripts/generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
from faker import Faker

fake = Faker()

class TransactionGenerator:
    """
    Generate realistic synthetic transaction data
    Includes both legitimate and fraudulent transactions
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        self.merchants = [
            "Amazon", "Walmart", "Target", "Starbucks", "Apple Store",
            "Netflix", "Uber", "Lyft", "DoorDash", "McDonald's",
            "CVS Pharmacy", "Walgreens", "Home Depot", "Lowe's",
            "Best Buy", "Kroger", "Costco", "Sam's Club", "Spotify",
            "Shell Gas", "Exxon", "Marriott", "Hilton", "Delta Airlines"
        ]
        
        self.countries = {
            "USA": 0.7,
            "UK": 0.1,
            "Canada": 0.08,
            "India": 0.05,
            "Germany": 0.04,
            "France": 0.03
        }
    
    def generate_card_profile(self, n_cards: int = 1000):
        """Generate profiles for cards"""
        cards = []
        for i in range(n_cards):
            cards.append({
                "card_id": f"CARD{i:08d}",
                "card_last4": f"{random.randint(1000, 9999)}",
                "cardholder_name": fake.name(),
                "avg_spend": np.random.exponential(100),
                "std_spend": np.random.exponential(30),
                "preferred_merchants": random.sample(self.merchants, k=random.randint(3, 10)),
                "preferred_country": np.random.choice(list(self.countries.keys()), p=list(self.countries.values())),
                "preferred_hours": (random.randint(8, 12), random.randint(18, 22)),  # (start, end)
                "is_compromised": np.random.choice([True, False], p=[0.01, 0.99])
            })
        return pd.DataFrame(cards)
    
    def generate_transactions(self, cards_df: pd.DataFrame, n_transactions: int = 10000) -> pd.DataFrame:
        """Generate transactions for given cards"""
        transactions = []
        
        # Fraud patterns
        fraud_patterns = {
            "high_amount": 0.3,
            "foreign_country": 0.25,
            "odd_hours": 0.2,
            "card_testing": 0.15,
            "merchant_mismatch": 0.1
        }
        
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(n_transactions):
            # Pick a random card
            card = cards_df.iloc[random.randint(0, len(cards_df)-1)]
            
            # Determine if fraud
            is_fraud = card['is_compromised'] or np.random.random() < 0.03  # 3% fraud rate
            
            # Base transaction details
            txn = {
                "transaction_id": f"TXN{uuid.uuid4().hex[:8].upper()}",
                "timestamp": start_date + timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                ),
                "card_last4": card['card_last4'],
                "amount": 0,
                "merchant": "",
                "country": "",
                "device_id": f"DEV{random.randint(1000, 9999)}",
                "ip_address": fake.ipv4(),
                "is_fraud": 1 if is_fraud else 0,
                "fraud_type": None,
                "risk_score": 0
            }
            
            if is_fraud:
                # Generate fraudulent transaction
                fraud_type = np.random.choice(
                    list(fraud_patterns.keys()),
                    p=list(fraud_patterns.values())
                )
                txn['fraud_type'] = fraud_type
                
                if fraud_type == "high_amount":
                    txn['amount'] = np.random.exponential(1000) + 500
                    txn['merchant'] = np.random.choice(self.merchants)
                    txn['country'] = card['preferred_country']
                    
                elif fraud_type == "foreign_country":
                    txn['amount'] = np.random.exponential(200)
                    txn['merchant'] = np.random.choice(self.merchants)
                    # Pick a country not preferred
                    other_countries = [c for c in self.countries.keys() if c != card['preferred_country']]
                    txn['country'] = np.random.choice(other_countries)
                    
                elif fraud_type == "odd_hours":
                    txn['amount'] = np.random.exponential(300)
                    txn['merchant'] = np.random.choice(self.merchants)
                    txn['country'] = card['preferred_country']
                    # Set hour outside preferred range
                    preferred_start, preferred_end = card['preferred_hours']
                    hour = random.choice([random.randint(0, preferred_start-1), 
                                        random.randint(preferred_end+1, 23)])
                    txn['timestamp'] = txn['timestamp'].replace(hour=hour)
                    
                elif fraud_type == "card_testing":
                    txn['amount'] = random.choice([1, 5, 10, 25])
                    txn['merchant'] = np.random.choice(self.merchants)
                    txn['country'] = card['preferred_country']
                    
                elif fraud_type == "merchant_mismatch":
                    txn['amount'] = np.random.exponential(400)
                    # Pick a merchant not preferred
                    other_merchants = [m for m in self.merchants if m not in card['preferred_merchants']]
                    txn['merchant'] = np.random.choice(other_merchants) if other_merchants else np.random.choice(self.merchants)
                    txn['country'] = card['preferred_country']
                
                txn['risk_score'] = random.randint(70, 100)
                
            else:
                # Generate legitimate transaction
                txn['amount'] = np.random.normal(card['avg_spend'], card['std_spend'])
                txn['amount'] = max(1, abs(txn['amount']))
                
                # Usually preferred merchant
                if random.random() < 0.8:
                    txn['merchant'] = np.random.choice(card['preferred_merchants'])
                else:
                    txn['merchant'] = np.random.choice(self.merchants)
                
                # Usually home country
                if random.random() < 0.9:
                    txn['country'] = card['preferred_country']
                else:
                    txn['country'] = np.random.choice(list(self.countries.keys()))
                
                txn['risk_score'] = random.randint(0, 30)
            
            transactions.append(txn)
        
        return pd.DataFrame(transactions)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = "transactions.csv"):
        """Save transactions to CSV"""
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} transactions to {filename}")
    
    def save_to_db(self, df: pd.DataFrame):
        """Save to SQLite database"""
        from src.core.database import db
        
        for _, row in df.iterrows():
            db.insert_transaction(row.to_dict())
        
        print(f"Saved {len(df)} transactions to database")

# Generate and save
if __name__ == "__main__":
    generator = TransactionGenerator()
    
    print("Generating card profiles...")
    cards = generator.generate_card_profile(500)
    
    print("Generating transactions...")
    transactions = generator.generate_transactions(cards, 50000)
    
    print(f"Fraud rate: {transactions['is_fraud'].mean()*100:.2f}%")
    print(f"Average amount: ${transactions['amount'].mean():.2f}")
    print(f"Total volume: ${transactions['amount'].sum():,.2f}")
    
    # Save
    generator.save_to_csv(transactions, "data/synthetic/transactions.csv")
