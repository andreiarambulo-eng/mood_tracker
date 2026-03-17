from routes.api import API
from fastapi.middleware.cors import CORSMiddleware

app = API().app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
