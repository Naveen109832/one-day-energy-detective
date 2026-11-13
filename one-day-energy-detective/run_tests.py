"""
Unified Test Runner for One-Day Energy Detective.
Executes all unit, integration, validation, and multi-tenant security test suites.
"""

import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def run_all_tests():
    print("=" * 65)
    print("  [*] Running One-Day Energy Detective Verification Test Suites")
    print("=" * 65)
    
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(PROJECT_ROOT / "backend" / "tests"), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 65)
    if result.wasSuccessful():
        print(f"  [SUCCESS] ALL {result.testsRun} TESTS PASSED SUCCESSFULLY!")
        print("=" * 65)
        return 0
    else:
        print(f"  [FAILURE] TEST SUITE FAILED: {len(result.failures)} failures, {len(result.errors)} errors.")
        print("=" * 65)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
