"""
Database performance optimization script
Run this to optimize your SQLite database for better performance
"""

import sqlite3
import os
from app import app

def optimize_database():
    """Optimize SQLite database for better performance"""
    
    db_path = os.path.join(app.instance_path, 'anime_site.db')
    community_db_path = os.path.join(app.instance_path, 'community.db')
    
    # Optimize main database
    if os.path.exists(db_path):
        print("Optimizing main database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode = WAL")
        
        # Optimize cache size (use more memory for better performance)
        cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Optimize synchronous mode
        cursor.execute("PRAGMA synchronous = NORMAL")
        
        # Optimize temp store
        cursor.execute("PRAGMA temp_store = MEMORY")
        
        # Analyze database for query optimizer
        cursor.execute("ANALYZE")
        
        # Vacuum database to reclaim space
        cursor.execute("VACUUM")
        
        conn.commit()
        conn.close()
        print("✅ Main database optimized!")
    
    # Optimize community database
    if os.path.exists(community_db_path):
        print("Optimizing community database...")
        conn = sqlite3.connect(community_db_path)
        cursor = conn.cursor()
        
        # Apply same optimizations
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA cache_size = -32000")  # 32MB cache
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.execute("PRAGMA temp_store = MEMORY")
        cursor.execute("ANALYZE")
        cursor.execute("VACUUM")
        
        conn.commit()
        conn.close()
        print("✅ Community database optimized!")
    
    print("\n🚀 Database optimization completed!")
    print("📝 Performance improvements applied:")
    print("   - WAL mode enabled for better concurrency")
    print("   - Increased cache size for faster queries")
    print("   - Optimized synchronous mode")
    print("   - Database analyzed and vacuumed")

if __name__ == '__main__':
    with app.app_context():
        optimize_database()
