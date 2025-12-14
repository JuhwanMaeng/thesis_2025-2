import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.v1.router import api_router
from app.memory.mongo.client import MongoClientManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 lifespan 관리."""
    os.makedirs(settings.faiss_index_dir, exist_ok=True)
    os.makedirs(settings.faiss_meta_dir, exist_ok=True)
    
    from app.memory.vector.faiss_manager import FAISSManager
    for index_name in ['episodic', 'persona', 'world']:
        manager = FAISSManager(index_name, settings.openai_embedding_dim)
        if manager.exists():
            try:
                manager.load_index()
            except ValueError as e:
                import logging
                logging.error(f"FAISS index {index_name} dimension mismatch: {str(e)}")
    
    MongoClientManager.initialize()
    
    yield
    
    MongoClientManager.close()


app = FastAPI(
    title="AI NPC Framework",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",  # Vite dev server alternate port
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


# Custom Swagger UI with dark theme
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    dark_theme_css = """
    <style>
      /* App dark mode colors: background: hsl(220 20% 8%), card: hsl(220 18% 11%), border: hsl(220 16% 18%), foreground: hsl(220 14% 96%) */
      body {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui {
        color: hsl(220, 14%, 96%) !important;
        background-color: hsl(220, 20%, 8%) !important;
      }
      .swagger-ui .topbar {
        background-color: hsl(220, 18%, 11%) !important;
        border-bottom: 1px solid hsl(220, 16%, 18%) !important;
      }
      .swagger-ui .topbar .download-url-wrapper {
        background-color: hsl(220, 18%, 11%) !important;
      }
      .swagger-ui .topbar .download-url-wrapper input {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
        border: 1px solid hsl(220, 16%, 18%) !important;
      }
      .swagger-ui .info {
        background-color: hsl(220, 18%, 11%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .info .title {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .scheme-container {
        background-color: hsl(220, 18%, 11%) !important;
      }
      .swagger-ui .opblock {
        background-color: hsl(220, 18%, 11%) !important;
        border-color: hsl(220, 16%, 18%) !important;
      }
      .swagger-ui .opblock.opblock-post {
        background-color: hsl(142, 76%, 20%) !important;
        border-color: hsl(142, 76%, 25%) !important;
      }
      .swagger-ui .opblock.opblock-get {
        background-color: hsl(199, 89%, 25%) !important;
        border-color: hsl(199, 89%, 30%) !important;
      }
      .swagger-ui .opblock.opblock-put {
        background-color: hsl(38, 92%, 25%) !important;
        border-color: hsl(38, 92%, 30%) !important;
      }
      .swagger-ui .opblock.opblock-delete {
        background-color: hsl(0, 72%, 25%) !important;
        border-color: hsl(0, 72%, 30%) !important;
      }
      .swagger-ui .opblock .opblock-summary {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .opblock-body {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .opblock-body pre {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .parameter__name {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .parameter__type {
        color: hsl(220, 10%, 55%) !important;
      }
      .swagger-ui .response-col_status {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .response-col_description {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .model-box {
        background-color: hsl(220, 18%, 11%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .model-title {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui table thead tr th {
        background-color: hsl(220, 18%, 11%) !important;
        color: hsl(220, 14%, 96%) !important;
        border-color: hsl(220, 16%, 18%) !important;
      }
      .swagger-ui table tbody tr td {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
        border-color: hsl(220, 16%, 18%) !important;
      }
      .swagger-ui input {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
        border-color: hsl(220, 16%, 18%) !important;
      }
      .swagger-ui select {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
        border-color: hsl(220, 16%, 18%) !important;
      }
      .swagger-ui textarea {
        background-color: hsl(220, 20%, 8%) !important;
        color: hsl(220, 14%, 96%) !important;
        border-color: hsl(220, 16%, 18%) !important;
      }
      .swagger-ui .btn {
        background-color: hsl(217, 91%, 60%) !important;
        color: hsl(0, 0%, 100%) !important;
      }
      .swagger-ui .btn:hover {
        background-color: hsl(217, 91%, 65%) !important;
      }
      .swagger-ui .btn.cancel {
        background-color: hsl(220, 16%, 16%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .btn.cancel:hover {
        background-color: hsl(220, 16%, 20%) !important;
      }
      .swagger-ui .response-col_status {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .opblock-description-wrapper,
      .swagger-ui .opblock-description {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .opblock-tag {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .opblock-tag-section {
        background-color: hsl(220, 20%, 8%) !important;
      }
      .swagger-ui .opblock-tag-section h4 {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .parameter__extension,
      .swagger-ui .parameter__in {
        color: hsl(220, 10%, 55%) !important;
      }
      .swagger-ui .prop-name {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .prop-type {
        color: hsl(220, 10%, 55%) !important;
      }
      .swagger-ui .prop-format {
        color: hsl(220, 10%, 55%) !important;
      }
      .swagger-ui code {
        background-color: hsl(220, 18%, 11%) !important;
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .highlight-code {
        background-color: hsl(220, 18%, 11%) !important;
      }
      .swagger-ui .response-content-type {
        color: hsl(220, 10%, 55%) !important;
      }
      .swagger-ui .response .response-col_status {
        color: hsl(220, 14%, 96%) !important;
      }
      .swagger-ui .response .response-col_description {
        color: hsl(220, 14%, 96%) !important;
      }
    </style>
    """
    
    html_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )
    # Inject dark theme CSS into the HTML
    html_content = html_response.body.decode('utf-8')
    html_content = html_content.replace('</head>', dark_theme_css + '</head>')
    return HTMLResponse(content=html_content)


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return HTMLResponse(
        """
    <!doctype html>
    <html lang="en">
      <head>
        <title>Swagger UI</title>
      </head>
      <body>
        <script>
          window.opener.postMessage({type: 'oauth2-redirect'}, '*');
          window.close();
        </script>
      </body>
    </html>
    """
    )


@app.get("/health")
async def root_health():
    """Root health check."""
    return {"status": "ok"}
