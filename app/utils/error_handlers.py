"""
error handling utilities for the premier league player role discovery app.

this module provides decorators and functions for graceful error handling
and defensive programming throughout the application.
"""

import functools
import traceback
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

import pandas as pd
import streamlit as st

from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

# type hint for decorated function
F = TypeVar('F', bound=Callable[..., Any])

def handle_exceptions(
    error_message: str = "An error occurred",
    fallback_return: Any = None,
    log_traceback: bool = True,
    show_streamlit_error: bool = True,
    expected_exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    decorator for handling exceptions in functions.
    
    args:
        error_message: user-friendly error message to display
        fallback_return: value to return if an exception occurs
        log_traceback: whether to log the full traceback
        show_streamlit_error: whether to show an error message in streamlit
        expected_exceptions: tuple of exception types to catch
        
    returns:
        decorated function with exception handling
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except expected_exceptions as e:
                if log_traceback:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}"
                    )
                else:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                
                if show_streamlit_error:
                    st.error(f"{error_message}: {str(e)}")
                
                return fallback_return
        return cast(F, wrapper)
    return decorator

def validate_dataframe(
    df: Optional[pd.DataFrame], 
    required_columns: list = None,
    min_rows: int = 1
) -> bool:
    """
    validate a pandas dataframe meets requirements.
    
    args:
        df: dataframe to validate
        required_columns: list of column names that must exist
        min_rows: minimum number of rows required
        
    returns:
        bool: whether the dataframe is valid
    """
    if df is None:
        logger.error("DataFrame is None")
        return False
    
    if len(df) < min_rows:
        logger.error(f"DataFrame has insufficient rows: {len(df)} < {min_rows}")
        return False
    
    if required_columns:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"DataFrame missing required columns: {missing_cols}")
            return False
    
    return True

def safe_get(
    data: Dict[str, Any], 
    key: str, 
    default: Any = None,
    expected_type: Optional[Type] = None
) -> Any:
    """
    safely get a value from a dictionary with type checking.
    
    args:
        data: dictionary to get value from
        key: key to look up
        default: default value if key doesn't exist
        expected_type: optional type to check against
        
    returns:
        value from dictionary or default
    """
    value = data.get(key, default)
    
    if expected_type and value is not None and not isinstance(value, expected_type):
        logger.warning(
            f"Type mismatch for key '{key}': expected {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
        return default
    
    return value
