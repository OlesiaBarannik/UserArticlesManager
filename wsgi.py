from userarticlesmanager.extensions import create_app
from userarticlesmanager.routes import register_routes

app = create_app()

# Register routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
