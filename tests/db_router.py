class DBRouter:

    def db_for_write(self, model, **hints):
        if model._meta.db_table == "post":
            return "other"
        return None

    def db_for_read(self, model, **hints):
        if model._meta.db_table == "post":
            return "other"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return (
            db == "default" and model_name != "post"
        )    or (
            db == "other" and model_name == "post"
        )
    