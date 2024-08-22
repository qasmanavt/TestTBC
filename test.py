import pandas as pd
import json
from datetime import datetime, timedelta

data = pd.read_csv('data.csv')

current_date = datetime.fromisoformat(data['application_date'].iloc[0])
current_date_naive = current_date.replace(tzinfo=None)

def parse_contract_json(contracts):
    try:
        contract_list = json.loads(contracts)
        if isinstance(contract_list, list) and all(isinstance(d, dict) for d in contract_list):
            return contract_list
        else:
            return []
    except (json.JSONDecodeError, TypeError):
        return []

data['parsed_contracts'] = data['contracts'].apply(parse_contract_json)

def calculate_features_from_parsed(row, current_date):
    contracts = row['parsed_contracts']
    if not contracts:
        return pd.Series({
            'tot_claim_cnt_l180d': -3,
            'disb_bank_loan_wo_tbc': -3,
            'day_sinlastloan': -3
        })
    
    tot_claim_cnt_l180d = 0
    disb_bank_loan_wo_tbc = 0
    last_loan_date = None
    
    for contract in contracts:
        try:
            contract_date = datetime.strptime(contract['claim_date'], '%d.%m.%Y')
        except (ValueError, KeyError):
            continue   
        
        bank = contract.get('bank', '')
        try:
            amount = int(contract.get('summa', 0)) if contract.get('summa') else 0
        except ValueError:
            amount = 0  
        
   
        if current_date - timedelta(days=180) <= contract_date <= current_date:
            tot_claim_cnt_l180d += 1
        
     
        if bank != "TBC":
            disb_bank_loan_wo_tbc += amount
            
    
        if last_loan_date is None or contract_date > last_loan_date:
            last_loan_date = contract_date
    
 
    day_sinlastloan = (current_date - last_loan_date).days if last_loan_date else -3
    
    return pd.Series({
        'tot_claim_cnt_l180d': tot_claim_cnt_l180d if tot_claim_cnt_l180d > 0 else -3,
        'disb_bank_loan_wo_tbc': disb_bank_loan_wo_tbc if disb_bank_loan_wo_tbc > 0 else -3,
        'day_sinlastloan': day_sinlastloan if day_sinlastloan >= 0 else -3
    })

 
features_final = data.apply(lambda row: calculate_features_from_parsed(row, current_date_naive), axis=1)
result_final = pd.concat([data[['id', 'application_date']], features_final], axis=1)
output_path_final = 'contract_features_final.csv'
result_final.to_csv(output_path_final, index=False)

