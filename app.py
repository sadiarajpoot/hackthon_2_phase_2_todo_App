from backend.src.main import app as fastapi_app

# For Hugging Face Spaces, we just need to expose the FastAPI app
# The Spaces environment will handle running the server
app = fastapi_app

# If you want to run this locally for testing, uncomment the following:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)