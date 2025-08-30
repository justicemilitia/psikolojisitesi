class MockDB:
    def __init__(self, app=None):
        self.app = app
    
    def init_app(self, app):
        pass
    
    def create_all(self):
        pass
    
    def session(self):
        return MockSession()

class MockSession:
    def __init__(self):
        pass
    
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def close(self):
        pass

def patch_app():
    import app
    app.db = MockDB()