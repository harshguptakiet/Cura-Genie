"""
Data Deduplication Service for CuraGenie

This service handles:
- PRS score deduplication
- Genomic variant deduplication
- Timeline event deduplication
- Data validation and cleanup
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import text, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.database_manager import get_db_context
from db.models import PRSScore, GenomicVariant, TimelineEvent, GenomicData, User

logger = logging.getLogger(__name__)

class DataDeduplicationService:
    """Service for deduplicating data across all entities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def deduplicate_prs_scores(self, user_id: Optional[int] = None) -> Dict[str, int]:
        """
        Remove duplicate PRS scores, keeping the most recent for each user/disease/file combination
        
        Args:
            user_id: Optional user ID to deduplicate for specific user only
            
        Returns:
            Dict with counts of deduplicated records
        """
        try:
            with get_db_context() as session:
                if user_id:
                    # Deduplicate for specific user
                    return self._deduplicate_user_prs_scores(session, user_id)
                else:
                    # Deduplicate for all users
                    return self._deduplicate_all_prs_scores(session)
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate PRS scores: {e}")
            raise
    
    def _deduplicate_user_prs_scores(self, session: Session, user_id: int) -> Dict[str, int]:
        """Deduplicate PRS scores for a specific user"""
        try:
            # Find duplicate scores for this user
            duplicates_query = text("""
                WITH ranked_scores AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY disease_type, genomic_data_id 
                               ORDER BY calculated_at DESC, id DESC
                           ) as rn
                    FROM prs_scores 
                    WHERE user_id = :user_id
                )
                SELECT id FROM ranked_scores WHERE rn > 1
            """)
            
            duplicates = session.execute(duplicates_query, {"user_id": user_id}).fetchall()
            duplicate_ids = [row[0] for row in duplicates]
            
            if not duplicate_ids:
                return {"deduplicated": 0, "kept": 0}
            
            # Delete duplicate scores
            delete_query = text("DELETE FROM prs_scores WHERE id = ANY(:duplicate_ids)")
            result = session.execute(delete_query, {"duplicate_ids": duplicate_ids})
            
            # Count remaining scores for this user
            kept_count = session.query(PRSScore).filter(PRSScore.user_id == user_id).count()
            
            self.logger.info(f"✅ Deduplicated {len(duplicate_ids)} PRS scores for user {user_id}")
            return {
                "deduplicated": len(duplicate_ids),
                "kept": kept_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate PRS scores for user {user_id}: {e}")
            raise
    
    def _deduplicate_all_prs_scores(self, session: Session) -> Dict[str, int]:
        """Deduplicate PRS scores for all users"""
        try:
            # Find all duplicate scores across all users
            duplicates_query = text("""
                WITH ranked_scores AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY user_id, disease_type, genomic_data_id 
                               ORDER BY calculated_at DESC, id DESC
                           ) as rn
                    FROM prs_scores
                )
                SELECT id FROM ranked_scores WHERE rn > 1
            """)
            
            duplicates = session.execute(duplicates_query).fetchall()
            duplicate_ids = [row[0] for row in duplicates]
            
            if not duplicate_ids:
                return {"deduplicated": 0, "kept": 0}
            
            # Delete duplicate scores
            delete_query = text("DELETE FROM prs_scores WHERE id = ANY(:duplicate_ids)")
            result = session.execute(delete_query, {"duplicate_ids": duplicate_ids})
            
            # Count remaining scores
            kept_count = session.query(PRSScore).count()
            
            self.logger.info(f"✅ Deduplicated {len(duplicate_ids)} PRS scores across all users")
            return {
                "deduplicated": len(duplicate_ids),
                "kept": kept_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate all PRS scores: {e}")
            raise
    
    def deduplicate_genomic_variants(self, genomic_data_id: Optional[int] = None) -> Dict[str, int]:
        """
        Remove duplicate genomic variants, keeping the highest quality version
        
        Args:
            genomic_data_id: Optional file ID to deduplicate for specific file only
            
        Returns:
            Dict with counts of deduplicated records
        """
        try:
            with get_db_context() as session:
                if genomic_data_id:
                    # Deduplicate for specific file
                    return self._deduplicate_file_variants(session, genomic_data_id)
                else:
                    # Deduplicate for all files
                    return self._deduplicate_all_variants(session)
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate genomic variants: {e}")
            raise
    
    def _deduplicate_file_variants(self, session: Session, genomic_data_id: int) -> Dict[str, int]:
        """Deduplicate variants for a specific genomic file"""
        try:
            # Find duplicate variants within this file
            duplicates_query = text("""
                WITH ranked_variants AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY chromosome, position, reference, alternative 
                               ORDER BY quality DESC NULLS LAST, id DESC
                           ) as rn
                    FROM genomic_variants 
                    WHERE genomic_data_id = :genomic_data_id
                )
                SELECT id FROM ranked_variants WHERE rn > 1
            """)
            
            duplicates = session.execute(duplicates_query, {"genomic_data_id": genomic_data_id}).fetchall()
            duplicate_ids = [row[0] for row in duplicates]
            
            if not duplicate_ids:
                return {"deduplicated": 0, "kept": 0}
            
            # Delete duplicate variants
            delete_query = text("DELETE FROM genomic_variants WHERE id = ANY(:duplicate_ids)")
            result = session.execute(delete_query, {"duplicate_ids": duplicate_ids})
            
            # Count remaining variants for this file
            kept_count = session.query(GenomicVariant).filter(
                GenomicVariant.genomic_data_id == genomic_data_id
            ).count()
            
            self.logger.info(f"✅ Deduplicated {len(duplicate_ids)} variants for file {genomic_data_id}")
            return {
                "deduplicated": len(duplicate_ids),
                "kept": kept_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate variants for file {genomic_data_id}: {e}")
            raise
    
    def _deduplicate_all_variants(self, session: Session) -> Dict[str, int]:
        """Deduplicate variants across all files"""
        try:
            # Find all duplicate variants across all files
            duplicates_query = text("""
                WITH ranked_variants AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY genomic_data_id, chromosome, position, reference, alternative 
                               ORDER BY quality DESC NULLS LAST, id DESC
                           ) as rn
                    FROM genomic_variants
                )
                SELECT id FROM ranked_variants WHERE rn > 1
            """)
            
            duplicates = session.execute(duplicates_query).fetchall()
            duplicate_ids = [row[0] for row in duplicates]
            
            if not duplicate_ids:
                return {"deduplicated": 0, "kept": 0}
            
            # Delete duplicate variants
            delete_query = text("DELETE FROM genomic_variants WHERE id = ANY(:duplicate_ids)")
            result = session.execute(delete_query, {"duplicate_ids": duplicate_ids})
            
            # Count remaining variants
            kept_count = session.query(GenomicVariant).count()
            
            self.logger.info(f"✅ Deduplicated {len(duplicate_ids)} variants across all files")
            return {
                "deduplicated": len(duplicate_ids),
                "kept": kept_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate all variants: {e}")
            raise
    
    def deduplicate_timeline_events(self, user_id: Optional[int] = None) -> Dict[str, int]:
        """
        Remove duplicate timeline events, keeping the most recent
        
        Args:
            user_id: Optional user ID to deduplicate for specific user only
            
        Returns:
            Dict with counts of deduplicated records
        """
        try:
            with get_db_context() as session:
                if user_id:
                    # Deduplicate for specific user
                    return self._deduplicate_user_timeline(session, user_id)
                else:
                    # Deduplicate for all users
                    return self._deduplicate_all_timeline(session)
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate timeline events: {e}")
            raise
    
    def _deduplicate_user_timeline(self, session: Session, user_id: int) -> Dict[str, int]:
        """Deduplicate timeline events for a specific user"""
        try:
            # Find duplicate events for this user (same type, title, and description within 1 hour)
            duplicates_query = text("""
                WITH ranked_events AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY event_type, title, description 
                               ORDER BY created_at DESC, id DESC
                           ) as rn
                    FROM timeline_events 
                    WHERE user_id = :user_id
                    AND created_at > NOW() - INTERVAL '1 hour'
                )
                SELECT id FROM ranked_events WHERE rn > 1
            """)
            
            duplicates = session.execute(duplicates_query, {"user_id": user_id}).fetchall()
            duplicate_ids = [row[0] for row in duplicates]
            
            if not duplicate_ids:
                return {"deduplicated": 0, "kept": 0}
            
            # Delete duplicate events
            delete_query = text("DELETE FROM timeline_events WHERE id = ANY(:duplicate_ids)")
            result = session.execute(delete_query, {"duplicate_ids": duplicate_ids})
            
            # Count remaining events for this user
            kept_count = session.query(TimelineEvent).filter(TimelineEvent.user_id == user_id).count()
            
            self.logger.info(f"✅ Deduplicated {len(duplicate_ids)} timeline events for user {user_id}")
            return {
                "deduplicated": len(duplicate_ids),
                "kept": kept_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate timeline for user {user_id}: {e}")
            raise
    
    def _deduplicate_all_timeline(self, session: Session) -> Dict[str, int]:
        """Deduplicate timeline events for all users"""
        try:
            # Find all duplicate events across all users
            duplicates_query = text("""
                WITH ranked_events AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY user_id, event_type, title, description 
                               ORDER BY created_at DESC, id DESC
                           ) as rn
                    FROM timeline_events
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                )
                SELECT id FROM ranked_events WHERE rn > 1
            """)
            
            duplicates = session.execute(duplicates_query).fetchall()
            duplicate_ids = [row[0] for row in duplicates]
            
            if not duplicate_ids:
                return {"deduplicated": 0, "kept": 0}
            
            # Delete duplicate events
            delete_query = text("DELETE FROM timeline_events WHERE id = ANY(:duplicate_ids)")
            result = session.execute(delete_query, {"duplicate_ids": duplicate_ids})
            
            # Count remaining events
            kept_count = session.query(TimelineEvent).count()
            
            self.logger.info(f"✅ Deduplicated {len(duplicate_ids)} timeline events across all users")
            return {
                "deduplicated": len(duplicate_ids),
                "kept": kept_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deduplicate all timeline events: {e}")
            raise
    
    def run_full_deduplication(self) -> Dict[str, Any]:
        """
        Run full deduplication across all entities
        
        Returns:
            Dict with deduplication results for all entities
        """
        try:
            self.logger.info("🚀 Starting full data deduplication...")
            
            results = {
                "prs_scores": {},
                "genomic_variants": {},
                "timeline_events": {},
                "total_deduplicated": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Deduplicate PRS scores
            results["prs_scores"] = self.deduplicate_prs_scores()
            
            # Deduplicate genomic variants
            results["genomic_variants"] = self.deduplicate_genomic_variants()
            
            # Deduplicate timeline events
            results["timeline_events"] = self.deduplicate_timeline_events()
            
            # Calculate total deduplicated records
            total_deduplicated = (
                results["prs_scores"].get("deduplicated", 0) +
                results["genomic_variants"].get("deduplicated", 0) +
                results["timeline_events"].get("deduplicated", 0)
            )
            results["total_deduplicated"] = total_deduplicated
            
            self.logger.info(f"🎉 Full deduplication completed! Total records deduplicated: {total_deduplicated}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Full deduplication failed: {e}")
            raise
    
    def get_duplication_report(self) -> Dict[str, Any]:
        """
        Generate a report on potential duplicate data
        
        Returns:
            Dict with duplication statistics
        """
        try:
            with get_db_context() as session:
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "potential_duplicates": {}
                }
                
                # Check for potential PRS score duplicates
                prs_duplicates_query = text("""
                    SELECT COUNT(*) as total,
                           COUNT(*) - COUNT(DISTINCT (user_id, disease_type, genomic_data_id)) as duplicates
                    FROM prs_scores
                """)
                prs_result = session.execute(prs_duplicates_query).fetchone()
                report["potential_duplicates"]["prs_scores"] = {
                    "total": prs_result[0],
                    "duplicates": prs_result[1]
                }
                
                # Check for potential variant duplicates
                variant_duplicates_query = text("""
                    SELECT COUNT(*) as total,
                           COUNT(*) - COUNT(DISTINCT (genomic_data_id, chromosome, position, reference, alternative)) as duplicates
                    FROM genomic_variants
                """)
                variant_result = session.execute(variant_duplicates_query).fetchone()
                report["potential_duplicates"]["genomic_variants"] = {
                    "total": variant_result[0],
                    "duplicates": variant_result[1]
                }
                
                # Check for potential timeline duplicates
                timeline_duplicates_query = text("""
                    SELECT COUNT(*) as total,
                           COUNT(*) - COUNT(DISTINCT (user_id, event_type, title, description)) as duplicates
                    FROM timeline_events
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                """)
                timeline_result = session.execute(timeline_duplicates_query).fetchone()
                report["potential_duplicates"]["timeline_events"] = {
                    "total": timeline_result[0],
                    "duplicates": timeline_result[1]
                }
                
                return report
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate duplication report: {e}")
            raise

# Global service instance
deduplication_service = DataDeduplicationService()
