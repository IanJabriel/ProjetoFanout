from datetime import datetime
from pydantic import BaseModel, validator

class ProdutoDTO(BaseModel):
    id: int
    nome: str
    preco: float
    porcentagem: int
    dataInicio: str
    dataFim: str

    @validator('porcentagem')
    def porcentagem_valida(cls, v):
        if v > 100:
            raise ValueError("Porcentagem não pode ser maior que 100")
        return v

    @validator('dataInicio', 'dataFim')
    def validar_data(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', ''))
            return v
        except ValueError:
            raise ValueError("Formato de data inválido. Use ISO 8601 (ex: '2023-05-01T00:00:00Z')")