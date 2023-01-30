class DBRouter:

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "other":
            return "post"
        return None
