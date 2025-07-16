from flask import Flask, request, jsonify
from core.pipeline_runner import PipelineRunner

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

if __name__ == "__main__":
    app.run(port=8000)
