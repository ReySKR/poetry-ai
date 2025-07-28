from pydantic import BaseModel, Field

class PoetryOutput(BaseModel):
    poetry_output: str = Field(description="Nutze dieses Feld für dein Gedicht")
    additions: str = Field(description="Nutze dieses Feld für zusätzliche Informationen, welche der Nutzer sehen soll. Beispiel: Rückfragen")
    is_final_poetry: bool = Field(description="Nutze dieses Feld um zu signalisieren, dass dies das finale Gedicht ohne jegliche 'additions' ist!")