from pydantic import BaseModel
from DTO.produtoDTO import ProdutoDTO

class PromocaoRequest(BaseModel):
    marca: str
    produtos: list[ProdutoDTO]

class PromocaoResponse(BaseModel):
    id: int
    marca: str
    nome: str
    produto_id: int
    porcentagem: int
    data_inicio: str
    data_fim: str
    data_registro: str