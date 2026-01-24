# ========================================
# 6. src/utils/date_parser.py
# ========================================

"""
Date parsing utilities for exam papers
"""

import re
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class DateParser:
    """Parse dates from exam paper filenames and content"""
    
    # Month name to number mapping
    MONTHS = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12,
    }
    
    @classmethod
    def parse_filename(cls, filename: str) -> Optional[Dict]:
        """
        Parse date from filename
        
        Example formats:
        - COS3701_OctNov_2025.pdf
        - COS3701_MayJune_2024.pdf
        - exam_2023_11.pdf
        """
        patterns = [
            # OctNov_2025 format
            r'([A-Z][a-z]{2,})([A-Z][a-z]{2,})_(\d{4})',
            # May_2024 format
            r'([A-Z][a-z]{2,})_(\d{4})',
            # 2024_11 format
            r'(\d{4})_(\d{1,2})',
            # 2024-11 format
            r'(\d{4})-(\d{1,2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    return cls._extract_date_from_match(match)
                except Exception as e:
                    logger.warning(f"Error parsing date from {filename}: {e}")
        
        return None
    
    @classmethod
    def _extract_date_from_match(cls, match) -> Dict:
        """Extract date information from regex match"""
        groups = match.groups()
        
        if len(groups) == 3:
            # Month1Month2_Year format
            month1 = cls.MONTHS.get(groups[0].lower())
            month2 = cls.MONTHS.get(groups[1].lower())
            year = int(groups[2])
            
            return {
                'year': year,
                'month_start': month1,
                'month_end': month2,
                'period': f"{groups[0]}-{groups[1]} {year}"
            }
        
        elif len(groups) == 2:
            if groups[0].isdigit():
                # Year_Month format
                year = int(groups[0])
                month = int(groups[1])
            else:
                # Month_Year format
                month = cls.MONTHS.get(groups[0].lower())
                year = int(groups[1])
            
            return {
                'year': year,
                'month': month,
                'period': f"{month}/{year}"
            }
        
        return None
    
    @classmethod
    def parse_exam_header(cls, text: str) -> Optional[Dict]:
        """Parse date from exam paper header/title"""
        # Look for date patterns in first 500 characters
        header = text[:500]
        
        patterns = [
            r'(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})',  # 15 October 2024
            r'([A-Z][a-z]+)\s+(\d{4})',  # October 2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, header)
            if match:
                groups = match.groups()
                
                if len(groups) == 3:
                    day = int(groups[0])
                    month = cls.MONTHS.get(groups[1].lower())
                    year = int(groups[2])
                    
                    return {
                        'day': day,
                        'month': month,
                        'year': year,
                        'date': f"{day}/{month}/{year}"
                    }
                
                elif len(groups) == 2:
                    month = cls.MONTHS.get(groups[0].lower())
                    year = int(groups[1])
                    
                    return {
                        'month': month,
                        'year': year,
                        'period': f"{groups[0]} {year}"
                    }
        
        return None