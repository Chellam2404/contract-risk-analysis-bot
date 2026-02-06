"""
Audit Logger - Log all user actions for compliance
"""
import json
import os
from datetime import datetime
from typing import Dict

def log_action(contract_id: str, action: str, metadata: Dict = None):
    """
    Log user action to audit trail
    
    Args:
        contract_id: Unique contract identifier
        action: Action type (upload, analyze, export, etc.)
        metadata: Additional context
    """
    log_dir = 'data/audit_logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'contract_id': contract_id,
        'action': action,
        'metadata': metadata or {}
    }
    
    # Append to daily log file
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'audit_{date_str}.jsonl')
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Failed to log action: {e}")

def get_contract_history(contract_id: str) -> list:
    """
    Retrieve audit history for a specific contract
    """
    log_dir = 'data/audit_logs'
    history = []
    
    if not os.path.exists(log_dir):
        return history
    
    # Search all log files
    for filename in os.listdir(log_dir):
        if filename.endswith('.jsonl'):
            filepath = os.path.join(log_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get('contract_id') == contract_id:
                            history.append(entry)
            except Exception as e:
                print(f"Failed to read log file {filename}: {e}")
    
    return sorted(history, key=lambda x: x['timestamp'])
