#!/usr/bin/env python3
"""
Database index creation script for performance optimization
Run this after updating the models to add database indexes
"""

from app import app, db
from models import User, Anime, Genre, Rating, Episode, News, Event, CommunityMember

def create_indexes():
    """Create database indexes for better performance"""
    with app.app_context():
        try:
            # Create indexes for User table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_user_username ON user (username)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_user_email ON user (email)'))
            
            # Create indexes for Anime table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_anime_name ON anime (name)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_anime_release_year ON anime (release_year)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_anime_status ON anime (status)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_anime_type ON anime (anime_type)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_anime_average_rating ON anime (average_rating)'))
            
            # Create indexes for Rating table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_rating_user_id ON rating (user_id)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_rating_anime_id ON rating (anime_id)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_rating_score ON rating (score)'))
            
            # Create indexes for Episode table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_episode_anime_id ON episode (anime_id)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_episode_number ON episode (number)'))
            
            # Create indexes for News table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news (timestamp)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_news_is_pinned ON news (is_pinned)'))
            
            # Create indexes for Event table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_event_start_time ON event (start_time)'))
            
            # Create indexes for CommunityMember table
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_community_member_email ON community_member (email)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_community_member_student_id ON community_member (student_id)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_community_member_is_approved ON community_member (is_approved)'))
            
            db.session.commit()
            print("✅ All database indexes created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")

if __name__ == '__main__':
    create_indexes()
