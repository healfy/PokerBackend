
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        workers=1,
        host="localhost",
        port=8001,
    )
