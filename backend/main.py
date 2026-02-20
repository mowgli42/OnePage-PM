"""
FastAPI backend for Project Management App.
Spec: openspec.md
"""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Project Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store with sample mock data
TODOS = [
    {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "Ship the app",
        "completed": False,
        "created_at": "2026-02-19T10:00:00Z",
    },
    {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "title": "Write OpenSpec",
        "completed": True,
        "created_at": "2026-02-19T09:00:00Z",
    },
    {
        "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "title": "Set up Beads tracker",
        "completed": True,
        "created_at": "2026-02-19T08:30:00Z",
    },
]


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    completed: bool = False


class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    completed: bool | None = None


class TodoResponse(BaseModel):
    id: str
    title: str
    completed: bool
    created_at: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoResponse])
def list_todos():
    return TODOS


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str):
    for t in TODOS:
        if t["id"] == todo_id:
            return t
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(body: TodoCreate):
    todo = {
        "id": str(uuid4()),
        "title": body.title,
        "completed": body.completed,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    TODOS.append(todo)
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, body: TodoUpdate):
    for i, t in enumerate(TODOS):
        if t["id"] == todo_id:
            if body.title is not None:
                TODOS[i]["title"] = body.title
            if body.completed is not None:
                TODOS[i]["completed"] = body.completed
            return TODOS[i]
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    for i, t in enumerate(TODOS):
        if t["id"] == todo_id:
            TODOS.pop(i)
            return
    raise HTTPException(status_code=404, detail="Todo not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
