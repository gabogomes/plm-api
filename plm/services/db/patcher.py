def apply_patch(entity, payload):
    changes = payload.dict(exclude_unset=True)

    items = changes.items()

    for key, value in items:
        setattr(entity, key, value)
