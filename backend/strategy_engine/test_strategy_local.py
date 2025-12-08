import asyncio
from . import driver

def test_dry_run():
    print("Running strategy engine dry-run test...")
    driver.main(execute=False)
    print("Dry-run test completed.")

if __name__ == "__main__":
    test_dry_run()
