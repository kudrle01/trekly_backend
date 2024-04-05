from fitness_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='10.0.1.20', debug=False)
