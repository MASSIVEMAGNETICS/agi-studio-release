from flask import Flask, request, jsonify
from core.pipeline_runner import PipelineRunner
from nodes.VictorModel import VictorModel

app = Flask(__name__)
runner = None

@app.route("/load_graph", methods=["POST"])
def load_graph():
    global runner
    graph_config = request.json
    runner = PipelineRunner(graph_config)
    return jsonify({"status": "loaded"})

@app.route("/run", methods=["POST"])
def run():
    result = runner.run_pipeline(request.json)
    return jsonify(result)

@app.route("/stop", methods=["POST"])
def stop():
    runner.stop_pipeline()
    return jsonify({"status": "stopped"})

@app.route('/victor/generate', methods=['POST'])
def victor_generate():
    data = request.json
    prompt = data.get('prompt', '')
    # Assume VictorModel node class or logic here
    output = VictorModel(node_id="victor", config={}).run({'prompt': prompt})
    return jsonify(output)

if __name__ == "__main__":
    app.run(port=8000)
