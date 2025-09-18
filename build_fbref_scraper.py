#!/usr/bin/env python3
"""
FBref Premier League Player Stats Scraper

This script scrapes player-level statistics from FBref.com for the Premier League
2024-2025 season and saves them as CSV files in the data/raw/fbref_2024_25/ directory.

Usage:
    python build_fbref_scraper.py [--tables TABLE1,TABLE2,...]

Options:
    --tables    Comma-separated list of specific tables to scrape
                (e.g., standard,shooting,passing)
"""

import os
import sys
import time
import logging
import argparse
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/fbref_scraper.log", mode="a"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define URLs for different stat tables - using 2023-2024 season (completed) instead of 2024-2025
url_map = {
    "standard": "https://fbref.com/en/comps/9/2023-2024/stats/2023-2024-Premier-League-Stats",
    "shooting": "https://fbref.com/en/comps/9/2023-2024/shooting/2023-2024-Premier-League-Stats",
    "passing": "https://fbref.com/en/comps/9/2023-2024/passing/2023-2024-Premier-League-Stats",
    "passing_types": "https://fbref.com/en/comps/9/2023-2024/passing_types/2023-2024-Premier-League-Stats",
    "gca": "https://fbref.com/en/comps/9/2023-2024/gca/2023-2024-Premier-League-Stats",
    "defense": "https://fbref.com/en/comps/9/2023-2024/defense/2023-2024-Premier-League-Stats",
    "possession": "https://fbref.com/en/comps/9/2023-2024/possession/2023-2024-Premier-League-Stats",
    "playing_time": "https://fbref.com/en/comps/9/2023-2024/playingtime/2023-2024-Premier-League-Stats",
    "misc": "https://fbref.com/en/comps/9/2023-2024/misc/2023-2024-Premier-League-Stats",
}

# Output directory
OUTPUT_DIR = "data/raw/fbref_2023_24"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_column_name(col: str) -> str:
    """
    Clean and normalize column names.
    
    Args:
        col: Original column name
        
    Returns:
        Cleaned column name
    """
    # Convert to lowercase
    col = col.lower()
    
    # Replace spaces with underscores
    col = col.replace(' ', '_')
    
    # Remove slashes and parentheses
    col = col.replace('/', '_per_')
    col = col.replace('(', '')
    col = col.replace(')', '')
    
    # Remove other special characters
    col = col.replace('%', 'pct')
    col = col.replace('+', 'plus')
    col = col.replace('-', '_')
    col = col.replace('.', '')
    
    # Remove any duplicate underscores
    while '__' in col:
        col = col.replace('__', '_')
    
    return col


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=20)  # Increased wait times
)
def fetch_url(url: str) -> str:
    """
    Fetch URL content with retry logic.
    
    Args:
        url: URL to fetch
        
    Returns:
        HTML content as string
    """
    # More realistic user agent with recent browser version
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://fbref.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    # Add a longer delay to be respectful to the server
    time.sleep(5)  # Increased from 2 to 5 seconds
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.text
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}, Status Code: {e.response.status_code}")
        logger.error(f"Response headers: {e.response.headers}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {str(e)}")
        raise


def is_player_row(row) -> bool:
    """
    Check if a table row is a player row (not a header, team total, etc.)
    
    Args:
        row: BeautifulSoup row element
        
    Returns:
        True if it's a player row, False otherwise
    """
    # Check if it has the data-stat attribute for player name
    if not row.find('th', {'data-stat': 'player'}):
        return False
    
    # Check if it's a header row
    if row.find('th', {'scope': 'col'}):
        return False
    
    # Check if it's a team row (usually has 'data-stat': 'squad' without 'data-stat': 'player')
    if row.find('th', {'data-stat': 'squad'}) and not row.find('th', {'data-stat': 'player'}):
        return False
    
    return True


def has_enough_minutes(row, min_minutes: int = 600) -> bool:
    """
    Check if a player has played at least the minimum minutes.
    
    Args:
        row: BeautifulSoup row element
        min_minutes: Minimum minutes required
        
    Returns:
        True if the player has played enough minutes, False otherwise
    """
    minutes_element = row.find('td', {'data-stat': 'minutes'})
    if not minutes_element:
        return False
    
    try:
        minutes = int(minutes_element.text.strip().replace(',', ''))
        return minutes >= min_minutes
    except (ValueError, TypeError):
        return False


def extract_table_data(soup: BeautifulSoup, table_id_prefix: str = "stats_") -> Tuple[List[str], List[List[str]]]:
    """
    Extract column headers and row data from the main stats table.
    
    Args:
        soup: BeautifulSoup object
        table_id_prefix: Prefix for the table ID
        
    Returns:
        Tuple of (headers, rows)
    """
    # Find the main stats table
    tables = soup.find_all('table', id=lambda x: x and x.startswith(table_id_prefix))
    
    if not tables:
        raise ValueError(f"No table found with ID prefix '{table_id_prefix}'")
    
    table = tables[0]  # Use the first matching table
    
    # Extract headers from the thead section
    headers = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find_all('th')
        headers = [h.get('data-stat', h.text.strip()) for h in header_row]
    
    # Clean up headers
    headers = [clean_column_name(h) for h in headers]
    
    # Extract data rows
    rows = []
    tbody = table.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            # Skip non-player rows and players with insufficient minutes
            if not is_player_row(tr) or not has_enough_minutes(tr):
                continue
            
            # Extract cell data
            row_data = []
            
            # Handle the player name column (usually a th element)
            player_cell = tr.find('th', {'data-stat': 'player'})
            if player_cell:
                player_name = player_cell.text.strip()
                row_data.append(player_name)
            
            # Handle all other columns (td elements)
            for td in tr.find_all('td'):
                cell_value = td.text.strip()
                row_data.append(cell_value)
            
            rows.append(row_data)
    
    return headers, rows


def scrape_fbref_table(name: str, url: str) -> pd.DataFrame:
    """
    Scrape a specific table from FBref and return as a DataFrame.
    
    Args:
        name: Table name
        url: URL to scrape
        
    Returns:
        DataFrame containing the scraped data
    """
    logger.info(f"Scraping {name} table from {url}")
    
    try:
        # Fetch the page content
        html_content = fetch_url(url)
        
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract the table data
        headers, rows = extract_table_data(soup)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Add source_table column
        df['source_table'] = name
        
        # Basic cleaning
        # Convert numeric columns to appropriate types
        for col in df.columns:
            # Skip non-numeric columns
            if col in ['player', 'squad', 'pos', 'source_table']:
                continue
            
            # Try to convert to numeric
            try:
                df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
            except (AttributeError, ValueError):
                pass
        
        logger.info(f"Successfully scraped {name} table: {len(df)} rows, {len(df.columns)} columns")
        return df
    
    except Exception as e:
        logger.error(f"Error scraping {name} table: {str(e)}")
        raise


def test_url_access():
    """
    Test if we can access FBref before starting the full scraping process.
    
    Returns:
        bool: True if access is successful, False otherwise
    """
    test_url = "https://fbref.com/en/"
    
    logger.info(f"Testing access to FBref with URL: {test_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        
        response = requests.get(test_url, headers=headers)
        response.raise_for_status()
        
        logger.info("Successfully accessed FBref")
        return True
    
    except Exception as e:
        logger.error(f"Failed to access FBref: {str(e)}")
        return False


def main(tables_to_scrape: Optional[List[str]] = None):
    """
    Main function to scrape all or specified tables and save to CSV.
    
    Args:
        tables_to_scrape: List of specific tables to scrape, or None for all tables
    """
    # Test access to FBref first
    if not test_url_access():
        logger.error("Cannot access FBref. Exiting.")
        return
    
    # Determine which tables to scrape
    if tables_to_scrape:
        # Filter the url_map to only include specified tables
        filtered_url_map = {k: v for k, v in url_map.items() if k in tables_to_scrape}
        if not filtered_url_map:
            logger.error(f"None of the specified tables {tables_to_scrape} found in url_map")
            return
        urls_to_scrape = filtered_url_map
    else:
        urls_to_scrape = url_map
    
    # Scrape each table
    for name, url in tqdm(urls_to_scrape.items(), desc="Scraping tables"):
        try:
            df = scrape_fbref_table(name, url)
            
            # Save to CSV
            output_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {name} data to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to process {name} table: {str(e)}")
    
    logger.info("Scraping completed")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scrape FBref Premier League player stats")
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of specific tables to scrape (e.g., standard,shooting,passing)"
    )
    
    args = parser.parse_args()
    
    # Extract specific tables if provided
    tables_to_scrape = None
    if args.tables:
        tables_to_scrape = [t.strip() for t in args.tables.split(',')]
        logger.info(f"Scraping specific tables: {tables_to_scrape}")
    
    # Run the main function
    main(tables_to_scrape)
