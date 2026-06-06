from src.custom_smth.tasks import task_interval_half_and_one_second
from src.openapi import APITag
from src.routing import APIRouter
from src.worker._enqueue import enqueue_task

router = APIRouter(prefix="/smth", tags=[APITag.public])


@router.get("/enqueue")
async def get_smth_and_enqueue() -> dict:
    print("First print")

    enqueue_task(task_interval_half_and_one_second, print_string="Not from scheduler")
    await task_interval_half_and_one_second.kiq(
        print_string="Not from scheduler and enqueue"
    )

    return {"Enqueued": "called for taskinthalf"}
