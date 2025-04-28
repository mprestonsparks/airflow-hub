"""
Date utility functions for common date operations across projects.
"""

from datetime import datetime, timedelta
import pytz


class DateUtils:
    """
    Utility class for date and time operations.
    
    This class provides static methods for common date operations used across projects.
    """
    
    @staticmethod
    def get_date_range(start_date, end_date=None, days=None):
        """
        Get a list of dates between start_date and end_date or start_date and start_date + days.
        
        Args:
            start_date (str or datetime): Start date in 'YYYY-MM-DD' format or as datetime.
            end_date (str or datetime, optional): End date in 'YYYY-MM-DD' format or as datetime.
            days (int, optional): Number of days to include (alternative to end_date).
            
        Returns:
            list: List of datetime objects for each day in the range.
            
        Raises:
            ValueError: If neither end_date nor days is provided.
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        if end_date is None and days is None:
            raise ValueError("Either end_date or days must be provided")
        
        if end_date is not None:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = start_date + timedelta(days=days)
        
        # Generate list of dates
        date_list = []
        current_date = start_date
        
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        return date_list
    
    @staticmethod
    def format_date(date_obj, format_str='%Y-%m-%d'):
        """
        Format a datetime object as a string.
        
        Args:
            date_obj (datetime): The datetime object to format.
            format_str (str, optional): Format string. Defaults to '%Y-%m-%d'.
            
        Returns:
            str: Formatted date string.
        """
        return date_obj.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str, format_str='%Y-%m-%d'):
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str (str): Date string to parse.
            format_str (str, optional): Format string. Defaults to '%Y-%m-%d'.
            
        Returns:
            datetime: Parsed datetime object.
        """
        return datetime.strptime(date_str, format_str)
    
    @staticmethod
    def get_first_day_of_month(date_obj=None):
        """
        Get the first day of the month for a given date.
        
        Args:
            date_obj (datetime, optional): Date to use. Defaults to current date.
            
        Returns:
            datetime: First day of the month.
        """
        if date_obj is None:
            date_obj = datetime.now()
        
        return date_obj.replace(day=1)
    
    @staticmethod
    def get_last_day_of_month(date_obj=None):
        """
        Get the last day of the month for a given date.
        
        Args:
            date_obj (datetime, optional): Date to use. Defaults to current date.
            
        Returns:
            datetime: Last day of the month.
        """
        if date_obj is None:
            date_obj = datetime.now()
        
        # Get first day of next month and subtract one day
        if date_obj.month == 12:
            next_month = date_obj.replace(year=date_obj.year + 1, month=1, day=1)
        else:
            next_month = date_obj.replace(month=date_obj.month + 1, day=1)
        
        return next_month - timedelta(days=1)
    
    @staticmethod
    def convert_timezone(date_obj, from_tz='UTC', to_tz='America/New_York'):
        """
        Convert a datetime from one timezone to another.
        
        Args:
            date_obj (datetime): Datetime object to convert.
            from_tz (str, optional): Source timezone. Defaults to 'UTC'.
            to_tz (str, optional): Target timezone. Defaults to 'America/New_York'.
            
        Returns:
            datetime: Converted datetime object.
        """
        # Ensure the datetime is timezone-aware
        if date_obj.tzinfo is None:
            date_obj = pytz.timezone(from_tz).localize(date_obj)
        
        # Convert to target timezone
        return date_obj.astimezone(pytz.timezone(to_tz))
    
    @staticmethod
    def get_business_days(start_date, end_date=None, days=None, holidays=None):
        """
        Get a list of business days (Monday to Friday) between two dates.
        
        Args:
            start_date (str or datetime): Start date.
            end_date (str or datetime, optional): End date.
            days (int, optional): Number of business days (alternative to end_date).
            holidays (list, optional): List of holiday dates to exclude.
            
        Returns:
            list: List of datetime objects for each business day.
        """
        # Get all days in the range
        all_days = DateUtils.get_date_range(start_date, end_date, days)
        
        # Filter to only business days
        business_days = [d for d in all_days if d.weekday() < 5]  # 0-4 = Monday-Friday
        
        # Exclude holidays if provided
        if holidays:
            # Convert string holidays to datetime if needed
            holiday_dates = []
            for holiday in holidays:
                if isinstance(holiday, str):
                    holiday_dates.append(datetime.strptime(holiday, '%Y-%m-%d').date())
                else:
                    holiday_dates.append(holiday.date())
            
            business_days = [d for d in business_days if d.date() not in holiday_dates]
        
        return business_days
