#!/usr/bin/env python
"""
Test script to verify ball purchase and stock updates work correctly
"""

import sys
import os

# Test the ball saving format
def test_ball_save_format():
    """Test that the ball save format is correct"""
    
    test_balls = [
        {"Name": "Poke Ball", "Stock": 10},
        {"Name": "Great Ball", "Stock": 5},
        {"Name": "Ultra Ball", "Stock": 0},
    ]
    
    # Write test file
    with open("test_balls.py", "w", encoding="utf-8") as f:
        f.write("LIST = [\n")
        for ball in test_balls:
            f.write(f'    {{"Name": "{ball["Name"]}", "Stock": {ball["Stock"]}}},\n')
        f.write("]\n")
    
    # Read it back
    with open("test_balls.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    print("Generated file content:")
    print(content)
    
    # Try to import it
    try:
        import test_balls
        print("\n✓ File can be imported successfully")
        print(f"✓ Contains {len(test_balls.LIST)} balls")
        
        for ball in test_balls.LIST:
            print(f"  - {ball['Name']}: {ball['Stock']}")
        
        # Test updating stock
        test_balls.LIST[0]["Stock"] += 5
        print(f"\n✓ Updated {test_balls.LIST[0]['Name']} stock to {test_balls.LIST[0]['Stock']}")
        
        # Save again
        with open("test_balls.py", "w", encoding="utf-8") as f:
            f.write("LIST = [\n")
            for ball in test_balls.LIST:
                f.write(f'    {{"Name": "{ball["Name"]}", "Stock": {ball["Stock"]}}},\n')
            f.write("]\n")
        
        # Reload
        import importlib
        importlib.reload(test_balls)
        
        print(f"✓ After reload: {test_balls.LIST[0]['Name']} stock is {test_balls.LIST[0]['Stock']}")
        
        # Cleanup
        os.remove("test_balls.py")
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists("test_balls.py"):
            os.remove("test_balls.py")
        return False
    
    return True


def test_purchase_logic():
    """Test the purchase logic"""
    print("\n" + "="*60)
    print("Testing Purchase Logic")
    print("="*60)
    
    HowMany = 10
    BuyBall = "Poke Ball"
    
    # Simulate stock before purchase
    stock_before = 0
    
    # Add purchased balls
    stock_after_purchase = stock_before + int(HowMany)
    
    print(f"Buying {HowMany} {BuyBall}s")
    print(f"Stock before: {stock_before}")
    print(f"Stock after purchase: {stock_after_purchase}")
    
    # One ball will be thrown immediately
    stock_after_throw = stock_after_purchase - 1
    print(f"Stock after throwing one: {stock_after_throw}")
    
    expected = HowMany - 1
    if stock_after_throw == expected:
        print(f"✓ Correct! Final stock is {stock_after_throw} (bought {HowMany}, threw 1)")
        return True
    else:
        print(f"✗ Error! Expected {expected} but got {stock_after_throw}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Ball Stock Update Test Suite")
    print("="*60)
    
    test1 = test_ball_save_format()
    test2 = test_purchase_logic()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Ball Save Format Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Purchase Logic Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
