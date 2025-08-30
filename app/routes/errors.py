from flask import render_template

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html', title='Page Not Found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return render_template('errors/500.html', title='Server Error'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        return render_template('errors/403.html', title='Forbidden'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 errors"""
        return render_template('errors/401.html', title='Unauthorized'), 401