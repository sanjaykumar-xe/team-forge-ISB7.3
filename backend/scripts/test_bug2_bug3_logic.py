"""
test_bug2_bug3_logic.py
Unit tests verifying word-boundary truncation (Bug 2) and comma-formatted market size parsing (Bug 3).
"""
import re
from services.text_utils import truncate_at_word_boundary


def test_word_boundary_truncation():
    print("\n--- TEST: Word-Boundary Truncation ---")
    
    # 1. Mid-word cutoff test on persona/problem description
    text = "Active solid-state Peltier thermoelectric cooling and dual-zone temperature regulation for menopausal night sweats"
    # Old hard [:60] would be: "Active solid-state Peltier thermoelectric cooling and dual-zo"
    res60 = truncate_at_word_boundary(text, max_length=60)
    print(f"Max 60 chars: '{res60}'")
    assert not res60.endswith("dual-zo"), "Should not cut 'dual-zone' mid-word!"
    assert res60 == "Active solid-state Peltier thermoelectric cooling and"
    assert " " not in res60[-1], "Should not have trailing space"

    # 2. Market size evidence quote test
    quote = (
        "The global market for Eco-Friendly Cleaning Products was valued at US$32.2 Billion in 2024 "
        "and is projected to reach USD 55.4 Billion by 2032, exhibiting a compound annual growth rate (CAGR) of 6.8% "
        "during the forecast period. Consumers are increasingly adopting sustainable refillable solutions."
    )
    # Old hard [:240] cut at char 240
    res240 = truncate_at_word_boundary(quote, max_length=240)
    print(f"\nQuote max 240 chars: '{res240}'")
    # Must end on sentence or complete word, never mid-word like "increas"
    last_word = res240.split()[-1].strip(".,")
    assert last_word in ["period", "Consumers", "adopting", "sustainable", "solutions"], f"Unexpected last word: {last_word}"
    print(f"Last word: '{last_word}' - clean boundary verified!")

    # 3. Short text should remain unchanged
    short = "Obsidian is a private, local-first note-taking tool."
    assert truncate_at_word_boundary(short, max_length=100) == short
    print("\n[PASS] All Word-Boundary Truncation tests passed.")


def test_comma_formatted_market_size_parsing():
    print("\n--- TEST: Comma-Formatted Market Size Parsing ---")
    
    pattern = re.compile(
        r'(?:(?:USD\s*|US\$\s*|\$\s*)((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*(Billion|Million|Trillion|B|M|T)?)'
        r'|'
        r'(?:((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*(Billion|Million|Trillion|B|M|T)\s*(?:USD|dollars|\$))',
        re.IGNORECASE
    )

    test_cases = [
        # (input_text, expected_val, expected_unit)
        ("The market was valued at USD 1,870 Million in 2024", "1,870", "Million"),
        ("Estimated at $1,870.5 Million with 12% CAGR", "1,870.5", "Million"),
        ("Projected to reach $1,870 Billion by 2035", "1,870", "Billion"),
        ("Valued at US$1,870 Million in recent reports", "1,870", "Million"),
        ("Market size of $12,450,000 in regional sales", "12,450,000", ""),
        ("Recorded 1,870 Million USD in total revenue", "1,870", "Million"),
        ("Valued at $101.81 Billion in 2024", "101.81", "Billion"),
        ("Estimated at USD 1.28B", "1.28", "B"),
    ]

    for text, exp_val, exp_unit in test_cases:
        matches = []
        for m in pattern.finditer(text):
            val = m.group(1) or m.group(3)
            unit = m.group(2) or m.group(4) or ""
            matches.append((val, unit))
        
        assert len(matches) > 0, f"Failed to match text: '{text}'"
        val, unit = matches[0]
        print(f"Text: '{text}' -> Matched: val='{val}', unit='{unit}' (Expected: '{exp_val}', '{exp_unit}')")
        assert val == exp_val, f"Expected val '{exp_val}', got '{val}'"
        assert unit.lower() == exp_unit.lower(), f"Expected unit '{exp_unit}', got '{unit}'"

    print("\n[PASS] All Comma-Formatted Market Size Parsing tests passed.")


if __name__ == "__main__":
    test_word_boundary_truncation()
    test_comma_formatted_market_size_parsing()
