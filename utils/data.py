def reconstruct_updated_data(old_fields, model, new_fields):
    old_fields_model = model(**old_fields) 
    updated_item = old_fields_model.model_copy(update=new_fields).model_dump()
    return updated_item