class BlogDatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'blog':
            if model.__name__ == 'Signup':
                return 'default'
            elif model.__name__ == 'Posts':
                return 'supabase'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'blog':
            if model.__name__ == 'Signup':
                return 'default'
            elif model.__name__ == 'Posts':
                return 'supabase'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
