import subprocess
import sys

def main():
    print("Starting AI Assistant Comparison Platform...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
