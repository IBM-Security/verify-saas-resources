# test_path.py
import sys
print("Current working dir:", sys.path[0])
print("Full sys.path:")
for p in sys.path:
    print("  ", p)

try:
    from util.config_loader import Config
    config = Config("../conf/application.yaml")
    print(config.data)
    print("→ Import succeeded!")
except ModuleNotFoundError as e:
    print("→ Still failing:", e)