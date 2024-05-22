from celery import Celery

celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task
def save_to_db(name, description):
    from main import database
    import asyncio
    query = "INSERT INTO animals(name, description) VALUES (:name, :description)"
    asyncio.run(database.execute(query, values={"name": name, "description": description}))
