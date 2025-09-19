# from dotenv import load_dotenv

from src.mypkg.httphello import httphello


def run():
    print("Entering main.py")
    httphello()


if __name__ == "__main__":
    run()
