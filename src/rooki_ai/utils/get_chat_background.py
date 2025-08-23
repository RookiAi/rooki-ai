import os
import json
import logging
import psycopg2
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_chat_background(user_id: str) -> str:
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        return False

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        logger.info(f"Connected to database to fetch chat background for user: {user_id}")

        # Get Messages of the user
        # Get all Message where userId = user_id in Message table
        messages_query = """
        SELECT id, role, channel, external_chat_id, external_message_id, 
               external_event_id, reply_to_message_id, text, created_at, edited_at
        FROM public."Message" 
        WHERE "userId" = %s
        ORDER BY created_at DESC
        LIMIT 50
        """
        cursor.execute(messages_query, (user_id,))
        message_records = cursor.fetchall()
        
        messages = []
        for record in message_records:
            messages.append({
                "id": record[0],
                "role": record[1],
                "channel": record[2],
                "external_chat_id": record[3],
                "external_message_id": record[4],
                "external_event_id": record[5],
                "reply_to_message_id": record[6],
                "text": record[7],
                "created_at": record[8].isoformat() if record[8] else None,
                "edited_at": record[9].isoformat() if record[9] else None
            })

        # Get ConvoSummary of the user
        # Get one ConvoSummary where userId = user_id in ConvoSummary table
        convo_summary_query = """
        SELECT summary 
        FROM public."ConvoSummary" 
        WHERE "userId" = %s
        """
        cursor.execute(convo_summary_query, (user_id,))
        convo_record = cursor.fetchone()
        
        convo_summary = convo_record[0] if convo_record else ""

        # Get all SuggestedCategory of the user
        # Get one voice of the user where userId = user_id in Voice table
        # Get all SuggestedCategory where voiceId = voice.id in SuggestedCategory table
        voice_query = """
        SELECT id 
        FROM public."Voice" 
        WHERE "userId" = %s
        """
        cursor.execute(voice_query, (user_id,))
        voice_record = cursor.fetchone()
        
        suggested_categories = []
        if voice_record:
            voice_id = voice_record[0]
            categories_query = """
            SELECT id, "createdAt", "updatedAt" 
            FROM public."SuggestedCategory" 
            WHERE "voiceId" = %s
            ORDER BY "createdAt" DESC
            """
            cursor.execute(categories_query, (voice_id,))
            category_records = cursor.fetchall()
            
            for record in category_records:
                suggested_categories.append({
                    "id": record[0],
                    "created_at": record[1].isoformat() if record[1] else None,
                    "updated_at": record[2].isoformat() if record[2] else None
                })
        suggested_categories = []

        response = {
            "messages": messages,
            "convo_summary": convo_summary,
            "suggested_categories": suggested_categories,
        }

        # Close connection
        cursor.close()
        conn.close()
        logger.info(f"Successfully fetched chat background for user: {user_id}")
        
        return response

    except Exception as e:
        logger.error(f"Error retrieving chat background: {e}")
        # Ensure connection is closed even if an error occurs
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
        return False
