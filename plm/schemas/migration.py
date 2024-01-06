from plm.models import CamelModel, SchemaVersion


class MigrationResponse(CamelModel):
    cluster_arn: str
    task_arn: str


class SchemaVersionResponse(SchemaVersion):
    pass
