import argparse
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.manus import Manus
from app.logger import add_log_callback, logger, remove_log_callback

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define a Pydantic model for the incoming request
class PromptRequest(BaseModel):
    prompt: str


@app.post("/process/")
async def process(request: PromptRequest):
    prompt = request.prompt

    # Create async stream for SSE
    async def event_stream():
        # Create a queue for messages
        queue = asyncio.Queue()

        # Register a callback to capture all log messages
        def log_callback(message):
            asyncio.create_task(queue.put(message))

        callback_id = add_log_callback(log_callback)

        agent = Manus()

        try:
            if not prompt.strip():
                logger.warning("Empty prompt provided.")
                yield "data: Empty prompt provided.\n\n"
                return

            # Log a starting message
            logger.info("Processing your request...")

            # Start the agent task
            agent_task = asyncio.create_task(agent.run(prompt))

            # Stream messages until agent is done
            while not agent_task.done() or not queue.empty():
                try:
                    # Try to get a message from the queue, but don't block indefinitely
                    message = await asyncio.wait_for(queue.get(), timeout=0.1)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    # No message received in the timeout period, continue the loop
                    if agent_task.done() and queue.empty():
                        break

            # Wait for agent to complete if it's not done yet
            if not agent_task.done():
                await agent_task

            # Final message
            logger.info("Request processing completed.")
            yield "data: Request processing completed.\n\n"

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg)
            yield f"data: {error_msg}\n\n"
        finally:
            # Clean up the callback
            remove_log_callback(callback_id)
            await agent.cleanup()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Define a Pydantic model for the incoming request
class PromptRequest(BaseModel):
    prompt: str


@app.post("/process/")
async def process(request: PromptRequest):
    prompt = request.prompt

    # Create async stream for SSE
    async def event_stream():
        # Create a queue for messages
        queue = asyncio.Queue()

        # Register a callback to capture all log messages
        def log_callback(message):
            asyncio.create_task(queue.put(message))

        callback_id = add_log_callback(log_callback)

        agent = Manus()

        try:
            if not prompt.strip():
                logger.warning("Empty prompt provided.")
                yield "data: Empty prompt provided.\n\n"
                return

            # Log a starting message
            logger.info("Processing your request...")

            # Start the agent task
            agent_task = asyncio.create_task(agent.run(prompt))

            # Stream messages until agent is done
            while not agent_task.done() or not queue.empty():
                try:
                    # Try to get a message from the queue, but don't block indefinitely
                    message = await asyncio.wait_for(queue.get(), timeout=0.1)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    # No message received in the timeout period, continue the loop
                    if agent_task.done() and queue.empty():
                        break

            # Wait for agent to complete if it's not done yet
            if not agent_task.done():
                await agent_task

            # Final message
            logger.info("Request processing completed.")
            yield "data: Request processing completed.\n\n"

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg)
            yield f"data: {error_msg}\n\n"
        finally:
            # Clean up the callback
            remove_log_callback(callback_id)
            await agent.cleanup()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
