from typing import List, Optional
from datetime import datetime
from app.database import get_database
from app.models.example import ExampleModel, ExampleCreate, ExampleUpdate
from bson import ObjectId


class ExampleService:
    @staticmethod
    async def create_example(data: ExampleCreate) -> ExampleModel:
        """예제 생성"""
        db = get_database()
        example_dict = {
            "name": data.name,
            "description": data.description,
            "created_at": datetime.now()
        }
        result = await db.examples.insert_one(example_dict)
        example_dict["_id"] = result.inserted_id
        return ExampleModel(**example_dict)

    @staticmethod
    async def get_example_by_id(example_id: str) -> Optional[ExampleModel]:
        """ID로 예제 조회"""
        db = get_database()
        example = await db.examples.find_one({"_id": ObjectId(example_id)})
        if example:
            example["id"] = str(example["_id"])
            return ExampleModel(**example)
        return None

    @staticmethod
    async def get_all_examples() -> List[ExampleModel]:
        """모든 예제 조회"""
        db = get_database()
        examples = await db.examples.find().to_list(length=100)
        result = []
        for example in examples:
            example["id"] = str(example["_id"])
            result.append(ExampleModel(**example))
        return result

    @staticmethod
    async def update_example(example_id: str, data: ExampleUpdate) -> Optional[ExampleModel]:
        """예제 업데이트"""
        db = get_database()
        update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
        if not update_data:
            return None
        
        result = await db.examples.find_one_and_update(
            {"_id": ObjectId(example_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["id"] = str(result["_id"])
            return ExampleModel(**result)
        return None

    @staticmethod
    async def delete_example(example_id: str) -> bool:
        """예제 삭제"""
        db = get_database()
        result = await db.examples.delete_one({"_id": ObjectId(example_id)})
        return result.deleted_count > 0

