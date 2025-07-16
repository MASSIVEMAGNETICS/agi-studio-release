import os
import subprocess
import sys

def install_dependencies():
    """Installs dependencies from requirements.txt."""
    print("--- Installing dependencies ---")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("--- Dependencies installed successfully ---")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def train_tokenizer():
    """Trains the tokenizer."""
    print("\n--- Training tokenizer ---")
    try:
        subprocess.check_call([sys.executable, "-m", "victor_gpt5.victor_tokenizer"])
        print("--- Tokenizer trained successfully ---")
    except subprocess.CalledProcessError as e:
        print(f"Error training tokenizer: {e}")
        sys.exit(1)

def main():
    """Main setup wizard."""
    print("--- Victor-GPT5 GODCORE Setup Wizard ---")

    # Step 1: Install dependencies
    install_dependencies()

    # Step 2: Train tokenizer
    train_tokenizer()

    print("\n--- Setup complete! ---")
    print("You can now run the AGI using the following commands:")
    print("  - Interactive CLI: python -m victor_gpt5.victor_ui interact")
    print("  - API Server: python -m victor_gpt5.victor_ui serve")

if __name__ == "__main__":
    main()
