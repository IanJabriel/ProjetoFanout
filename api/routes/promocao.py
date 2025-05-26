from fastapi import APIRouter, HTTPException
from DTO.promocaoDTO import PromocaoRequest, PromocaoResponse
from typing import List
from database.database import init_db, insert_promocao, get_all_promocoes, sobreposicao_promocao

router = APIRouter()
init_db() 

@router.post("/receberPromocao/")
async def receber_promocao(promocao: PromocaoRequest):
    erros = []
    produtos_processados = 0


    for produto in promocao.produtos:
        if produto.porcentagem > 100:
            erros.append(f"Produto {produto.nome}: porcentagem inválida (>100%)")
            continue

        if sobreposicao_promocao(produto.id, produto.dataInicio, produto.dataFim):
            erros.append(
                f"Produto {produto.nome}: já existe promoção ativa para este produto "
                f"no período de {produto.dataInicio} a {produto.dataFim}"
            )
            continue

        sucesso = insert_promocao(promocao.marca, produto.dict())
        if not sucesso:
            erros.append(f"Produto {produto.nome}: erro ao salvar promoção")
        else:
            produtos_processados += 1

    if erros:
        raise HTTPException(
            status_code=409 if any("já existe promoção ativa" in e for e in erros) else 400,
            detail={
                "status": "parcial" if produtos_processados > 0 else "erro",
                "mensagem": f"{produtos_processados} produto(s) processado(s) com sucesso",
                "erros": erros
            }
        )

    return {
        "status": "sucesso",
        "mensagem": "Todos os produtos salvos com sucesso"
    }

@router.get("/promocoes/", response_model=List[PromocaoResponse])
def listar_promocoes():
    promocoes = get_all_promocoes()
    return promocoes