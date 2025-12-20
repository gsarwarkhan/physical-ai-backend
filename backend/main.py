from flask import Flask

# This creates a basic Flask web server application.
app = Flask(__name__)

@app.route("/")
def hello_world():
    """This function runs when you access the root URL ('/')."""
    return "<p>Hello, from the backend!</p>"

def main():
    """Main entry point for the backend server application."""
    # The server will run on port 8080 and automatically reload on code changes.
    app.run(debug=True, port=8080)

if __name__ == "__main__":
    # This block ensures that the main() function is called only when
    # the script is executed directly.
    main()
