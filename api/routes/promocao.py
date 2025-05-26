from fastapi import APIRouter, HTTPException
from DTO.promocaoDTO import PromocaoRequest, PromocaoResponse
from typing import List
from database.database import init_db, insert_promocao, get_all_promocoes

router = APIRouter()
init_db() 

@router.post("/receberPromocao/")
async def receber_promocao(promocao: PromocaoRequest):
    erros = []
    for produto in promocao.produtos:
        if produto.porcentagem > 100:
            erros.append(f"Produto {produto.nome}: porcentagem inválida (>100%)")
            continue

        sucesso = insert_promocao(promocao.marca, produto.dict())
        if not sucesso:
            erros.append(f"Produto {produto.nome}: promoção duplicada")

    if erros:
        raise HTTPException(status_code=409, detail=erros)

    return {
        "status": "sucesso",
        "mensagem": "Todos os produtos salvos com sucesso"
    }

@router.get("/promocoes/", response_model=List[PromocaoResponse])
def listar_promocoes():
    promocoes = get_all_promocoes()
    return promocoes