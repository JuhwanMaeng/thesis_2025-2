from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.example import ExampleModel, ExampleCreate, ExampleUpdate
from app.services.example_service import ExampleService

router = APIRouter()


@router.post("/", response_model=ExampleModel, status_code=status.HTTP_201_CREATED)
async def create_example(data: ExampleCreate):
    """예제 생성"""
    return await ExampleService.create_example(data)


@router.get("/", response_model=List[ExampleModel])
async def get_all_examples():
    """모든 예제 조회"""
    return await ExampleService.get_all_examples()


@router.get("/{example_id}", response_model=ExampleModel)
async def get_example(example_id: str):
    """ID로 예제 조회"""
    example = await ExampleService.get_example_by_id(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return example


@router.put("/{example_id}", response_model=ExampleModel)
async def update_example(example_id: str, data: ExampleUpdate):
    """예제 업데이트"""
    example = await ExampleService.update_example(example_id, data)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return example


@router.delete("/{example_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_example(example_id: str):
    """예제 삭제"""
    success = await ExampleService.delete_example(example_id)
    if not success:
        raise HTTPException(status_code=404, detail="Example not found")
    return None

