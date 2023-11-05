from .app import App
from .presentation.commands.music import *
from .presentation.commands.chat import *


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
