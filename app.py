from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder

app = Flask(__name__)


def create_engine_with_ssh():
    # SSH tunneling configuration
    server = SSHTunnelForwarder(
        ('185.151.213.119', 7025),
        ssh_username="konatus_site",
        ssh_password="nHcLM9$vfh9_wql9",
        remote_bind_address=('localhost', 5432)
    )

    server.start()

    # Create SQLAlchemy engine with SSH tunnel
    local_port = str(server.local_bind_port)
    db_uri = f"postgresql://postgres:postgres@127.0.0.1:{local_port}/Base6.5"
    engine = create_engine(db_uri)

    return engine, server


def execute_select_query(engine, query):
    with engine.connect() as connection:
        result = connection.execute(text(query)).fetchall()
        return result


@app.route('/test', methods=['GET'])
def test_query():
    engine, server = create_engine_with_ssh()

    # Test SELECT query
    select_query = "SELECT * FROM attribut;"
    result = execute_select_query(engine, select_query)

    server.stop()

    # Format the result as a JSON response
    columns = result[0].keys() if result else []
    data = [dict(zip(columns, row)) for row in result]

    return jsonify({"data": data})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
