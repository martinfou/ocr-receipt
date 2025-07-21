from ocr_receipt.config import ConfigManager

def main():
    config = ConfigManager()
    print("App mode:", config.get("app.mode", "not set"))
    # Future: pass config to CLI or GUI main class

if __name__ == "__main__":
    main() 