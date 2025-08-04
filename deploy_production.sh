#!/bin/bash

# Production deployment optimization script for Anime Fansub Platform
# Run this script to prepare your application for production

echo "🚀 Starting production optimization..."

# 1. Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# 2. Set production environment variables
echo "⚙️  Setting production environment..."
export FLASK_ENV=production
export FLASK_DEBUG=False

# 3. Database optimizations
echo "🗄️  Optimizing databases..."
python optimize_database.py

# 4. Create database indexes
echo "📊 Creating database indexes..."
python create_indexes_migration.py

# 5. Clear any existing cache
echo "🧹 Clearing cache..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 6. Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p instance

# 7. Set proper file permissions
echo "🔒 Setting file permissions..."
chmod 644 *.py
chmod 755 *.sh
chmod 600 instance/*.db 2>/dev/null || true

# 8. Optimize static files (if you have any minification tools)
echo "📄 Optimizing static files..."
# You can add CSS/JS minification here if needed
# Example: uglifyjs static/js/*.js -o static/js/app.min.js

# 9. Production recommendations
echo ""
echo "✅ Production optimization completed!"
echo ""
echo "📋 Additional recommendations for production:"
echo "   1. Use a reverse proxy (nginx) in front of Flask"
echo "   2. Use a WSGI server like Gunicorn or uWSGI"
echo "   3. Enable HTTPS with SSL certificates"
echo "   4. Set up log rotation"
echo "   5. Monitor application performance"
echo "   6. Set up database backups"
echo ""
echo "🚀 Example production command:"
echo "   gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "🔧 For nginx configuration, create:"
echo "   /etc/nginx/sites-available/anime-fansub"
