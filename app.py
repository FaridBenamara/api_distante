from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder
import json
import pandas as pd
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
        result_proxy = connection.execute(text(query))
        return result_proxy
def calculer_ev_projet(engine):
    query_work_elements = "SELECT * FROM attribut;"
    work_elements = pd.read_sql_query(query_work_elements, engine)

    # Calculer le p_acc(WE) × Valeur(WE) pour chaque work_element
    work_elements['ev'] = work_elements['percent_accomplished'] * work_elements['attributevalue']

    # Calculer la somme des produits pour obtenir la Valeur Économique du projet
    ev_projet = work_elements['ev'].sum()

    return jsonify({"ev_projet": ev_projet})
@app.route('/test', methods=['GET'])
def test_query():
    engine, server = create_engine_with_ssh()

    try:
        # Test SELECT query
        select_query = "SELECT weid, load_engage FROM attribut;"
        result_proxy = execute_select_query(engine, select_query)

        # Obtenez les noms de colonnes directement à partir de l'objet ResultProxy
        column_names = result_proxy.keys()

        # Récupérez les résultats sous forme de dictionnaires
        data = [dict(zip(column_names, row)) for row in result_proxy.fetchall()]

        # Manually serialize data to JSON
        json_data = json.dumps({"data": data})

        return json_data
    finally:
        server.stop()
@app.route('/ev_projet', methods=['GET'])
def ev_projet_route():
    engine, _ = create_engine_with_ssh()
    result = calculer_ev_projet(engine)
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
