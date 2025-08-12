"""
Blog System Example using PyMongo
=================================

A complete blog system with:
- User management
- Articles with categories and tags
- Comments system
- Search functionality
- User analytics

Author: PyMongo Examples
Date: 2025
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from datetime import datetime, timedelta
import re
from bson import ObjectId
from typing import List, Dict, Optional

class BlogSystem:
    """Complete blog system using MongoDB"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        """Initialize blog system"""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client.blog_system
            
            # Collections
            self.users = self.db.users
            self.articles = self.db.articles
            self.comments = self.db.comments
            self.categories = self.db.categories
            
            # Setup indexes
            self._setup_indexes()
            
            print("✅ Blog system initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing blog system: {e}")
            raise
    
    def _setup_indexes(self):
        """Setup database indexes for performance"""
        try:
            # User indexes
            self.users.create_index("email", unique=True)
            self.users.create_index("username", unique=True)
            
            # Article indexes
            self.articles.create_index([("title", TEXT), ("content", TEXT)])
            self.articles.create_index("author_id")
            self.articles.create_index("category")
            self.articles.create_index("tags")
            self.articles.create_index("published_date", direction=DESCENDING)
            self.articles.create_index("status")
            
            # Comment indexes
            self.comments.create_index("article_id")
            self.comments.create_index("author_id")
            self.comments.create_index("created_date", direction=DESCENDING)
            
            print("✅ Database indexes created")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
    
    # ================================
    # User Management
    # ================================
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str, bio: str = "") -> Optional[str]:
        """Create new user"""
        try:
            user_data = {
                "username": username,
                "email": email,
                "password": password,  # In production, hash this!
                "full_name": full_name,
                "bio": bio,
                "created_date": datetime.utcnow(),
                "last_login": None,
                "article_count": 0,
                "comment_count": 0,
                "followers": [],
                "following": [],
                "profile_image": None,
                "is_active": True
            }
            
            result = self.users.insert_one(user_data)
            print(f"✅ User '{username}' created successfully")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            user = self.users.find_one({
                "username": username,
                "password": password,
                "is_active": True
            })
            
            if user:
                # Update last login
                self.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
                print(f"✅ User '{username}' logged in successfully")
                return user
            else:
                print("❌ Invalid username or password")
                return None
                
        except Exception as e:
            print(f"❌ Error authenticating user: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile with statistics"""
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            
            if user:
                # Get user statistics
                article_count = self.articles.count_documents({"author_id": user_id})
                comment_count = self.comments.count_documents({"author_id": user_id})
                
                # Update statistics
                self.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "article_count": article_count,
                            "comment_count": comment_count
                        }
                    }
                )
                
                user["article_count"] = article_count
                user["comment_count"] = comment_count
                
                return user
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting user profile: {e}")
            return None
    
    # ================================
    # Article Management
    # ================================
    
    def create_article(self, title: str, content: str, author_id: str,
                      category: str, tags: List[str], status: str = "draft") -> Optional[str]:
        """Create new article"""
        try:
            article_data = {
                "title": title,
                "content": content,
                "author_id": author_id,
                "category": category,
                "tags": tags,
                "status": status,  # draft, published, archived
                "created_date": datetime.utcnow(),
                "published_date": datetime.utcnow() if status == "published" else None,
                "updated_date": datetime.utcnow(),
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "likes": [],
                "featured": False,
                "meta_description": content[:160] + "..." if len(content) > 160 else content,
                "reading_time": self._calculate_reading_time(content)
            }
            
            result = self.articles.insert_one(article_data)
            print(f"✅ Article '{title}' created successfully")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error creating article: {e}")
            return None
    
    def publish_article(self, article_id: str) -> bool:
        """Publish article"""
        try:
            result = self.articles.update_one(
                {"_id": ObjectId(article_id)},
                {
                    "$set": {
                        "status": "published",
                        "published_date": datetime.utcnow(),
                        "updated_date": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                print("✅ Article published successfully")
                return True
            else:
                print("❌ Article not found")
                return False
                
        except Exception as e:
            print(f"❌ Error publishing article: {e}")
            return False
    
    def get_articles(self, page: int = 1, limit: int = 10, 
                    category: str = None, author_id: str = None,
                    status: str = "published") -> List[Dict]:
        """Get articles with pagination and filtering"""
        try:
            # Build query
            query = {"status": status}
            
            if category:
                query["category"] = category
            
            if author_id:
                query["author_id"] = author_id
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Get articles with author information
            pipeline = [
                {"$match": query},
                {"$sort": {"published_date": -1}},
                {"$skip": skip},
                {"$limit": limit},
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"author_id": {"$toObjectId": "$author_id"}},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$author_id"]}}},
                            {"$project": {"username": 1, "full_name": 1, "profile_image": 1}}
                        ],
                        "as": "author"
                    }
                },
                {"$unwind": "$author"}
            ]
            
            articles = list(self.articles.aggregate(pipeline))
            return articles
            
        except Exception as e:
            print(f"❌ Error getting articles: {e}")
            return []
    
    def get_article_by_id(self, article_id: str, increment_views: bool = True) -> Optional[Dict]:
        """Get article by ID"""
        try:
            # Increment view count if requested
            if increment_views:
                self.articles.update_one(
                    {"_id": ObjectId(article_id)},
                    {"$inc": {"view_count": 1}}
                )
            
            # Get article with author information
            pipeline = [
                {"$match": {"_id": ObjectId(article_id)}},
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"author_id": {"$toObjectId": "$author_id"}},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$author_id"]}}},
                            {"$project": {"username": 1, "full_name": 1, "profile_image": 1, "bio": 1}}
                        ],
                        "as": "author"
                    }
                },
                {"$unwind": "$author"}
            ]
            
            result = list(self.articles.aggregate(pipeline))
            return result[0] if result else None
            
        except Exception as e:
            print(f"❌ Error getting article: {e}")
            return None
    
    def search_articles(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search articles by title and content"""
        try:
            pipeline = [
                {
                    "$match": {
                        "$text": {"$search": search_term},
                        "status": "published"
                    }
                },
                {"$sort": {"score": {"$meta": "textScore"}}},
                {"$limit": limit},
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"author_id": {"$toObjectId": "$author_id"}},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$author_id"]}}},
                            {"$project": {"username": 1, "full_name": 1}}
                        ],
                        "as": "author"
                    }
                },
                {"$unwind": "$author"}
            ]
            
            articles = list(self.articles.aggregate(pipeline))
            return articles
            
        except Exception as e:
            print(f"❌ Error searching articles: {e}")
            return []
    
    def like_article(self, article_id: str, user_id: str) -> bool:
        """Like/unlike article"""
        try:
            article = self.articles.find_one({"_id": ObjectId(article_id)})
            
            if not article:
                print("❌ Article not found")
                return False
            
            likes = article.get("likes", [])
            
            if user_id in likes:
                # Unlike
                result = self.articles.update_one(
                    {"_id": ObjectId(article_id)},
                    {
                        "$pull": {"likes": user_id},
                        "$inc": {"like_count": -1}
                    }
                )
                print("👎 Article unliked")
            else:
                # Like
                result = self.articles.update_one(
                    {"_id": ObjectId(article_id)},
                    {
                        "$push": {"likes": user_id},
                        "$inc": {"like_count": 1}
                    }
                )
                print("👍 Article liked")
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error liking article: {e}")
            return False
    
    # ================================
    # Comment Management
    # ================================
    
    def add_comment(self, article_id: str, author_id: str, content: str,
                   parent_id: str = None) -> Optional[str]:
        """Add comment to article"""
        try:
            comment_data = {
                "article_id": article_id,
                "author_id": author_id,
                "content": content,
                "parent_id": parent_id,  # For nested comments
                "created_date": datetime.utcnow(),
                "updated_date": datetime.utcnow(),
                "like_count": 0,
                "likes": [],
                "is_approved": True
            }
            
            result = self.comments.insert_one(comment_data)
            
            # Update article comment count
            self.articles.update_one(
                {"_id": ObjectId(article_id)},
                {"$inc": {"comment_count": 1}}
            )
            
            print("✅ Comment added successfully")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return None
    
    def get_comments(self, article_id: str) -> List[Dict]:
        """Get comments for article"""
        try:
            pipeline = [
                {"$match": {"article_id": article_id, "is_approved": True}},
                {"$sort": {"created_date": 1}},
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"author_id": {"$toObjectId": "$author_id"}},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$author_id"]}}},
                            {"$project": {"username": 1, "full_name": 1, "profile_image": 1}}
                        ],
                        "as": "author"
                    }
                },
                {"$unwind": "$author"}
            ]
            
            comments = list(self.comments.aggregate(pipeline))
            return self._organize_comments(comments)
            
        except Exception as e:
            print(f"❌ Error getting comments: {e}")
            return []
    
    def _organize_comments(self, comments: List[Dict]) -> List[Dict]:
        """Organize comments in hierarchical structure"""
        comment_map = {}
        root_comments = []
        
        # Create comment map
        for comment in comments:
            comment["replies"] = []
            comment_map[str(comment["_id"])] = comment
        
        # Organize hierarchy
        for comment in comments:
            if comment["parent_id"]:
                parent = comment_map.get(comment["parent_id"])
                if parent:
                    parent["replies"].append(comment)
            else:
                root_comments.append(comment)
        
        return root_comments
    
    # ================================
    # Analytics and Statistics
    # ================================
    
    def get_popular_articles(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get popular articles by views and likes"""
        try:
            date_threshold = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "status": "published",
                        "published_date": {"$gte": date_threshold}
                    }
                },
                {
                    "$addFields": {
                        "popularity_score": {
                            "$add": [
                                {"$multiply": ["$view_count", 1]},
                                {"$multiply": ["$like_count", 3]},
                                {"$multiply": ["$comment_count", 2]}
                            ]
                        }
                    }
                },
                {"$sort": {"popularity_score": -1}},
                {"$limit": limit},
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"author_id": {"$toObjectId": "$author_id"}},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$author_id"]}}},
                            {"$project": {"username": 1, "full_name": 1}}
                        ],
                        "as": "author"
                    }
                },
                {"$unwind": "$author"}
            ]
            
            articles = list(self.articles.aggregate(pipeline))
            return articles
            
        except Exception as e:
            print(f"❌ Error getting popular articles: {e}")
            return []
    
    def get_blog_statistics(self) -> Dict:
        """Get overall blog statistics"""
        try:
            stats = {}
            
            # Basic counts
            stats["total_users"] = self.users.count_documents({"is_active": True})
            stats["total_articles"] = self.articles.count_documents({"status": "published"})
            stats["total_comments"] = self.comments.count_documents({"is_approved": True})
            
            # Article statistics
            article_stats = list(self.articles.aggregate([
                {"$match": {"status": "published"}},
                {
                    "$group": {
                        "_id": None,
                        "total_views": {"$sum": "$view_count"},
                        "total_likes": {"$sum": "$like_count"},
                        "avg_reading_time": {"$avg": "$reading_time"}
                    }
                }
            ]))
            
            if article_stats:
                stats.update(article_stats[0])
                del stats["_id"]
            
            # Top categories
            top_categories = list(self.articles.aggregate([
                {"$match": {"status": "published"}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]))
            
            stats["top_categories"] = top_categories
            
            # Top authors
            top_authors = list(self.articles.aggregate([
                {"$match": {"status": "published"}},
                {"$group": {"_id": "$author_id", "article_count": {"$sum": 1}}},
                {"$sort": {"article_count": -1}},
                {"$limit": 5},
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"author_id": {"$toObjectId": "$_id"}},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$author_id"]}}},
                            {"$project": {"username": 1, "full_name": 1}}
                        ],
                        "as": "author"
                    }
                },
                {"$unwind": "$author"}
            ]))
            
            stats["top_authors"] = top_authors
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    # ================================
    # Utility Methods
    # ================================
    
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes"""
        words = len(content.split())
        # Average reading speed: 200 words per minute
        reading_time = max(1, round(words / 200))
        return reading_time
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        try:
            categories = self.articles.distinct("category", {"status": "published"})
            return sorted(categories)
            
        except Exception as e:
            print(f"❌ Error getting categories: {e}")
            return []
    
    def get_tags(self) -> List[str]:
        """Get all available tags"""
        try:
            tags = self.articles.distinct("tags", {"status": "published"})
            return sorted(tags)
            
        except Exception as e:
            print(f"❌ Error getting tags: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()
        print("✅ Database connection closed")


def demo_blog_system():
    """Demonstration of blog system functionality"""
    
    print("=" * 50)
    print("🌟 Blog System Demo")
    print("=" * 50)
    
    # Initialize blog system
    blog = BlogSystem()
    
    try:
        # Create users
        print("\n📝 Creating users...")
        user1_id = blog.create_user(
            username="john_doe",
            email="john@example.com",
            password="password123",
            full_name="John Doe",
            bio="Tech enthusiast and blogger"
        )
        
        user2_id = blog.create_user(
            username="jane_smith",
            email="jane@example.com",
            password="password456",
            full_name="Jane Smith",
            bio="Developer and writer"
        )
        
        # Create articles
        print("\n📰 Creating articles...")
        article1_id = blog.create_article(
            title="Introduction to MongoDB",
            content="MongoDB is a popular NoSQL database that provides high performance, high availability, and easy scalability. In this comprehensive guide, we'll explore the fundamentals of MongoDB and how to use it effectively in your applications.",
            author_id=user1_id,
            category="Technology",
            tags=["mongodb", "database", "nosql", "tutorial"],
            status="published"
        )
        
        article2_id = blog.create_article(
            title="Python Best Practices",
            content="Writing clean, maintainable Python code is essential for any developer. This article covers the most important best practices that every Python developer should follow, including code style, testing, and performance optimization.",
            author_id=user2_id,
            category="Programming",
            tags=["python", "best-practices", "clean-code"],
            status="published"
        )
        
        # Add comments
        print("\n💬 Adding comments...")
        comment1_id = blog.add_comment(
            article_id=article1_id,
            author_id=user2_id,
            content="Great article! Very informative and well-written."
        )
        
        comment2_id = blog.add_comment(
            article_id=article1_id,
            author_id=user1_id,
            content="Thanks for the feedback! Glad you found it helpful.",
            parent_id=comment1_id
        )
        
        # Like articles
        print("\n👍 Liking articles...")
        blog.like_article(article1_id, user2_id)
        blog.like_article(article2_id, user1_id)
        
        # Search articles
        print("\n🔍 Searching articles...")
        search_results = blog.search_articles("MongoDB database")
        print(f"Found {len(search_results)} articles matching 'MongoDB database'")
        
        # Get articles
        print("\n📖 Getting latest articles...")
        articles = blog.get_articles(limit=5)
        for article in articles:
            print(f"- {article['title']} by {article['author']['full_name']}")
            print(f"  Views: {article['view_count']}, Likes: {article['like_count']}")
        
        # Get article details
        print(f"\n📄 Article details for '{articles[0]['title']}':")
        article_details = blog.get_article_by_id(str(articles[0]['_id']))
        if article_details:
            print(f"Author: {article_details['author']['full_name']}")
            print(f"Category: {article_details['category']}")
            print(f"Tags: {', '.join(article_details['tags'])}")
            print(f"Reading time: {article_details['reading_time']} minutes")
        
        # Get comments
        print(f"\n💬 Comments for '{article_details['title']}':")
        comments = blog.get_comments(str(article_details['_id']))
        for comment in comments:
            print(f"- {comment['author']['full_name']}: {comment['content']}")
            for reply in comment['replies']:
                print(f"  └─ {reply['author']['full_name']}: {reply['content']}")
        
        # Get popular articles
        print("\n🔥 Popular articles (last 7 days):")
        popular = blog.get_popular_articles(days=7, limit=3)
        for article in popular:
            print(f"- {article['title']} (Score: {article['popularity_score']})")
        
        # Get statistics
        print("\n📊 Blog statistics:")
        stats = blog.get_blog_statistics()
        print(f"Total users: {stats.get('total_users', 0)}")
        print(f"Total articles: {stats.get('total_articles', 0)}")
        print(f"Total comments: {stats.get('total_comments', 0)}")
        print(f"Total views: {stats.get('total_views', 0)}")
        print(f"Average reading time: {stats.get('avg_reading_time', 0):.1f} minutes")
        
        print("\nTop categories:")
        for cat in stats.get('top_categories', []):
            print(f"- {cat['_id']}: {cat['count']} articles")
        
        # Get user profile
        print(f"\n👤 User profile for {user1_id}:")
        profile = blog.get_user_profile(user1_id)
        if profile:
            print(f"Username: {profile['username']}")
            print(f"Full name: {profile['full_name']}")
            print(f"Articles: {profile['article_count']}")
            print(f"Comments: {profile['comment_count']}")
        
        print("\n✅ Blog system demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    finally:
        blog.close_connection()


if __name__ == "__main__":
    demo_blog_system()
