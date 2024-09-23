import jwt, datetime, os
from flask import Flask, request
import psycopg2
from psycopg2.extras import RealDictCursor

server = Flask(__name__)

# Global variable to hold the database connection
db_connection = None


def init_db():
    """Initialize the database connection and store it globally."""
    global db_connection
    db_connection = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        dbname=os.environ.get("POSTGRES_DB"),
        port=int(os.environ.get("POSTGRES_PORT")),
        cursor_factory=RealDictCursor,  # Return results as dictionaries
    )


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # Use the global database connection
    cur = db_connection.cursor()

    # Check db for username and password
    cur.execute("SELECT email, password FROM users WHERE email=%s", (auth.username,))
    user_row = cur.fetchone()

    if user_row:
        email = user_row['email']
        password = user_row['password']

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        return "token expired", 403
    except jwt.InvalidTokenError:
        return "not authorized", 403

    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    # Initialize database connection at startup
    init_db()

    # Start the Flask server
    server.run(host="0.0.0.0", port=5001)
