from sqlalchemy.orm import declarative_base
import sqlalchemy

Base = declarative_base()

class Reloads(Base):
    __tablename__ = "reloads_tasks_2023_05_10"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key= True)
    issue = sqlalchemy.Column(sqlalchemy.String(length=40), unique= True)
    updated = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    created = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    elapsed_time = sqlalchemy.Column(sqlalchemy.String(length=40))
    instance_name = sqlalchemy.Column(sqlalchemy.String(length=40))
    task_type = sqlalchemy.Column(sqlalchemy.String(length=40))
    summary = sqlalchemy.Column(sqlalchemy.String(length=400))
    status = sqlalchemy.Column(sqlalchemy.String(length=40))
    creator = sqlalchemy.Column(sqlalchemy.String(length=40))
    assigneer = sqlalchemy.Column(sqlalchemy.String(length=40))
    
    def __str__(self) -> str:
        return f'{self.id}: {self.issue},{self.updated},{self.created},{self.elapsed_time},{self.instance_name},{self.task_type},{self.summary},{self.status},{self.creator},{self.assigneer}'

def create_tables(engine):
    Base.metadata.create_all(engine)