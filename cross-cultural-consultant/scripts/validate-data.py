#!/usr/bin/env python3
"""Verify the Hofstede data file can be loaded and all countries have valid dimensions."""

import json, sys, os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'hofstede-dimensions.json')

def validate():
    errors = []
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    countries = data.get('countries', {})
    print(f"Loaded {len(countries)} countries from {data.get('source', 'unknown')}")
    print(f"Snapshot: {data.get('scraped_at', 'unknown')}")
    
    required_dims = ['power_distance', 'individualism', 'motivation',
                     'uncertainty_avoidance', 'long_term_orientation', 'indulgence']
    
    for name, info in countries.items():
        dims = info.get('dimensions', {})
        missing = [d for d in required_dims if d not in dims]
        if missing:
            errors.append(f"{name}: missing dimensions {missing}")
    
    if errors:
        print(f"\n{len(errors)} countries with issues:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"All {len(countries)} countries have complete 6 dimensions.")
        sys.exit(0)

if __name__ == '__main__':
    validate()
