import os
import json
import logging
import psycopg2
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_voice_config_in_supabase(x_handle: str, positioning: str, tone: str, voice_config: dict):
    """
    Update the voice table in Supabase with the generated voice config.
    
    Args:
        x_handle: Twitter handle to update
        positioning: Positioning statement
        tone: Tone description
        voice_config: Complete voice configuration JSON
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        Exception: If there's an error updating the database
    """
    # Get PostgreSQL connection string from environment variables
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
        
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if record exists for this x_handle
        check_query = 'SELECT id FROM public."Voice" WHERE x_handle = %s'
        cursor.execute(check_query, (x_handle,))
        existing_record = cursor.fetchone()
        
        now = datetime.utcnow()
        
        if existing_record:
            # Update existing record
            update_query = '''
            UPDATE public."Voice" 
            SET positioning = %s, 
                tone = %s, 
                voice_config = %s, 
                "updatedAt" = %s
            WHERE x_handle = %s
            '''
            cursor.execute(
                update_query, 
                (
                    positioning, 
                    json.dumps({"description": tone}), 
                    json.dumps(voice_config), 
                    now, 
                    x_handle
                )
            )
            logger.info(f"Updated voice config for x_handle: {x_handle}")
        else:
            # Insert new record with a generated UUID
            import uuid
            new_id = str(uuid.uuid4())
            
            # This assumes there's a default user ID to associate with new records
            # Adjust this as needed for your specific requirements
            default_user_id = os.environ.get("DEFAULT_USER_ID", "system")
            
            insert_query = '''
            INSERT INTO public."Voice" (
                id, "userId", x_handle, positioning, tone, voice_config, "createdAt", "updatedAt"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(
                insert_query,
                (
                    new_id, 
                    default_user_id,
                    x_handle,
                    positioning, 
                    json.dumps({"description": tone}), 
                    json.dumps(voice_config), 
                    now, 
                    now
                )
            )
            logger.info(f"Created new voice config for x_handle: {x_handle}")
        
        # Commit the transaction
        conn.commit()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database error updating voice config: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error updating voice config: {str(e)}")
        return False