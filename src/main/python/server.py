from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CommitData(BaseModel):
    repo_name: str
    file_name: str
    commit_id: str
    commit_message: str
    commit_diff: str

@app.post("/analyze")
def analyze_commit(data: CommitData):
    ai_explanation = "No significant issues detected."
    affected_line = 0

    return {
        "aiExplanation": ai_explanation,
        "affectedLine": affected_line
    }
