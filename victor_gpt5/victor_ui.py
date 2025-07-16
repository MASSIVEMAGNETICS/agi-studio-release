import sys
import threading
import time
import yaml
import uvicorn
import typer
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add parent directory to path to allow local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from victor_gpt5.victor_agi import VictorAGIRouter

# --- Globals ---
CONFIG = None
AGI_INSTANCE = None
CLI_APP = typer.Typer()

# --- FastAPI Setup ---
api_app = FastAPI(
    title="Victor-GPT5 (GODCORE) API",
    description="Interface to the Victor-GPT5 Artificial General Intelligence.",
    version="1.0.0-GODCORE"
)

class PromptRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"

class PromptResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str

@api_app.on_event("startup")
def load_agi():
    global AGI_INSTANCE, CONFIG
    print("Loading GODCORE into API server...")
    with open("./victor_gpt5/configs/gpt5_victor.yaml", 'r') as f:
        CONFIG = yaml.safe_load(f)
    AGI_INSTANCE = VictorAGIRouter(CONFIG)
    print("GODCORE is online and integrated with the API.")

@api_app.post("/prompt", response_model=PromptResponse)
async def handle_prompt(request: PromptRequest):
    """Receives a prompt and returns the AGI's response."""
    if not AGI_INSTANCE:
        return {"error": "AGI not initialized"}, 503

    response_text = AGI_INSTANCE.route(request.prompt)

    return PromptResponse(
        response=response_text,
        user_id=request.user_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@api_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if not AGI_INSTANCE:
        await websocket.send_text("Error: AGI not initialized.")
        await websocket.close()
        return

    await websocket.send_text("Victor-GPT5 WebSocket connection established. Awaiting prompt.")
    while True:
        try:
            prompt = await websocket.receive_text()
            response = AGI_INSTANCE.route(prompt)
            await websocket.send_text(response)
        except Exception as e:
            await websocket.send_text(f"Connection closed or error: {e}")
            break

@api_app.get("/", response_class=HTMLResponse)
async def root():
    # Simple HTML interface for testing
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Victor-GPT5 GODCORE</title>
        </head>
        <body>
            <h1>Victor-GPT5 (GODCORE) is Online</h1>
            <p>Use the /docs endpoint for API documentation or connect via CLI/WebSocket.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- Typer CLI Setup ---
@CLI_APP.command()
def interact():
    """Start an interactive command-line session with Victor."""
    global AGI_INSTANCE, CONFIG
    if not AGI_INSTANCE:
        print("Initializing GODCORE for CLI session...")
        with open("./victor_gpt5/configs/gpt5_victor.yaml", 'r') as f:
            CONFIG = yaml.safe_load(f)
        AGI_INSTANCE = VictorAGIRouter(CONFIG)

    print("\n--- Victor-GPT5 Interactive CLI ---")
    print("Type 'exit' or 'quit' to end the session.")
    while True:
        prompt = input("You: ")
        if prompt.lower() in ['exit', 'quit']:
            print("Victor: Goodbye. Saving memory state.")
            AGI_INSTANCE.memory.save()
            break
        response = AGI_INSTANCE.route(prompt)
        print(f"Victor: {response}")

@CLI_APP.command()
def train(corpus: str = typer.Argument(..., help="Path to the training text file.")):
    """Fine-tune or train the model on a new corpus."""
    from victor_gpt5.victor_trainer import VictorTrainer
    global AGI_INSTANCE, CONFIG
    if not AGI_INSTANCE:
        print("Initializing GODCORE for training...")
        with open("./victor_gpt5/configs/gpt5_victor.yaml", 'r') as f:
            CONFIG = yaml.safe_load(f)
        AGI_INSTANCE = VictorAGIRouter(CONFIG)

    trainer = VictorTrainer(AGI_INSTANCE.model, AGI_INSTANCE.tokenizer, CONFIG)
    trainer.train(corpus)

@CLI_APP.command()
def evaluate():
    """Run the built-in evaluation suite."""
    from victor_gpt5.victor_eval import VictorEvaluator
    global AGI_INSTANCE, CONFIG
    if not AGI_INSTANCE:
        print("Initializing GODCORE for evaluation...")
        with open("./victor_gpt5/configs/gpt5_victor.yaml", 'r') as f:
            CONFIG = yaml.safe_load(f)
        AGI_INSTANCE = VictorAGIRouter(CONFIG)

    evaluator = VictorEvaluator(AGI_INSTANCE)
    evaluator.run_evaluation()

@CLI_APP.command()
def serve():
    """Launch the FastAPI server."""
    global CONFIG
    if not CONFIG:
        with open("./victor_gpt5/configs/gpt5_victor.yaml", 'r') as f:
            CONFIG = yaml.safe_load(f)

    ui_config = CONFIG['ui']
    print(f"--- Launching Victor-GPT5 API Server on http://{ui_config['host']}:{ui_config['port']} ---")
    uvicorn.run(api_app, host=ui_config['host'], port=ui_config['port'], log_level=ui_config['log_level'])

if __name__ == "__main__":
    CLI_APP()
