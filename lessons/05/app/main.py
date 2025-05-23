from fastapi import FastAPI, HTTPException, status
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from tracing import setup_otel
from celery.result import AsyncResult
from worker_make_lucky_numbers import app as celery_app
from worker_make_lucky_numbers.app import generate_lucky_numbers
from pydantic import BaseModel
import os


setup_otel('fastapi')
app = FastAPI()

# Instrument FastAPI application
FastAPIInstrumentor.instrument_app(app)
LoggingInstrumentor().instrument(set_logging_format=True) # Instrument logging

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI root!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q, "message": "Hello from FastAPI items!"}


class RandomNumbersRequest(BaseModel):
    length: int

class RandomNumbersResponse(BaseModel):
    # This model now directly includes the list of numbers
    numbers: list[int]

@app.post("/generate-lucky-numbers/", response_model=RandomNumbersResponse)
async def create_lucky_numbers_task(request: RandomNumbersRequest):
    """
    Triggers a Celery task to generate a list of random numbers and waits for the result.
    """
    if request.length <= 0:
        raise HTTPException(status_code=400, detail="Length must be a positive integer.")

    # Get timeout from environment variable or set a default (e.g., 30 seconds)
    # Convert to float for result.get()
    celery_timeout = float(os.getenv("CELERY_TASK_TIMEOUT", 30))

    try:
        # Send the task and immediately wait for its result
        # The .get() method will block until the task is complete or timeout is reached.
        result_async = generate_lucky_numbers.delay(request.length)
        random_numbers_list = result_async.get(timeout=celery_timeout)

        if result_async.successful():
            return {"numbers": random_numbers_list}
        else:
            # Handle potential task failure
            # result_async.traceback contains the traceback if the task failed
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Celery task failed: {result_async.info}" # info usually holds the exception
            )

    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, # 504 Gateway Timeout is appropriate for upstream timeouts
            detail=f"Celery task timed out after {celery_timeout} seconds. Task ID: {result_async.id}"
        )
    except Exception as e:
        # Catch any other exceptions that might occur during task execution or retrieval
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the task: {e}"
        )
