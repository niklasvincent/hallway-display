from server import create_app

import sys

app = create_app()

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print("Failed to start API server: {}".format(e), file=sys.stderr)
