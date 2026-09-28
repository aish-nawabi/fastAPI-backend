from fastapi import FastAPI
from src.routers import data_handler
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="CAG Project API Chatwith your pdf.",
    description="API for uploading PDFs, querying content via LLM, and managing data.",
    version="0.1.0",
)
app.include_router(
    data_handler.router,
    prefix="/api/v1",
    tags=["data handling and chats with PDF"],
)
@app.get("/",response_class=HTMLResponse, tags=["Root"])
def read_root():
    """
    provides a simple HTML welcome page with a link to the swagger (OpenAPI) docs.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>CAG Project API</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 2rem; background: #f9f9f9}
          .container { max-width: 600px; margin: auto; background: #fff; padding: 2rem; bord}
          h1 { color: #333; }
          a { color: #007acc; text-decoration: none; }
          a:hover { text-decoration: underline; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Welcome to the CAG project API</h1>
          <p> view the automatically generated API documentation here:</p>
          <p><a href="/docs" target="_blank">Swagger UI (OpenApi Docs)</p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, host="127.0.0.1", port=8001
    )


