import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re

class CSVAnalyzer:
    """Analyzes CSV data structure and provides insights."""
    
    def __init__(self):
        self.date_patterns = [
            r'\d{4}[-/]\d{2}[-/]\d{2}',  # YYYY-MM-DD or YYYY/MM/DD
            r'\d{2}[-/]\d{2}[-/]\d{4}',  # MM-DD-YYYY or MM/DD/YYYY
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # M-D-YYYY or M/D/YYYY
        ]
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the structure and content of a DataFrame."""
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage': self._get_memory_usage(df),
            'columns': {},
            'text_columns': [],
            'numeric_columns': [],
            'date_columns': [],
            'total_missing_values': df.isnull().sum().sum()
        }
        
        for column in df.columns:
            col_analysis = self._analyze_column(df[column])
            analysis['columns'][column] = col_analysis
            
            # Categorize columns
            if col_analysis['type'] == 'text':
                analysis['text_columns'].append(column)
            elif col_analysis['type'] == 'numeric':
                analysis['numeric_columns'].append(column)
            elif col_analysis['type'] == 'datetime':
                analysis['date_columns'].append(column)
        
        return analysis
    
    def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze a single column of data."""
        col_info = {
            'type': self._detect_column_type(series),
            'non_null_count': series.count(),
            'null_count': series.isnull().sum(),
            'unique_count': series.nunique(),
            'sample_values': self._get_sample_values(series)
        }
        
        # Add type-specific analysis
        if col_info['type'] == 'numeric':
            col_info.update(self._analyze_numeric_column(series))
        elif col_info['type'] == 'text':
            col_info.update(self._analyze_text_column(series))
        elif col_info['type'] == 'datetime':
            col_info.update(self._analyze_datetime_column(series))
        
        return col_info
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """Detect the type of data in a column."""
        # Remove null values for analysis
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return 'empty'
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        
        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Check if string data contains dates
        if self._contains_dates(non_null_series):
            return 'datetime'
        
        # Check if string data can be converted to numeric
        try:
            pd.to_numeric(non_null_series, errors='raise')
            return 'numeric'
        except (ValueError, TypeError):
            pass
        
        return 'text'
    
    def _contains_dates(self, series: pd.Series) -> bool:
        """Check if a text series contains date-like patterns."""
        sample_size = min(100, len(series))
        sample_values = series.head(sample_size).astype(str)
        
        date_matches = 0
        for value in sample_values:
            for pattern in self.date_patterns:
                if re.search(pattern, value):
                    date_matches += 1
                    break
        
        # Consider it a date column if more than 50% of samples match date patterns
        return date_matches / sample_size > 0.5
    
    def _get_sample_values(self, series: pd.Series, n: int = 5) -> List[Any]:
        """Get sample values from a series."""
        non_null_values = series.dropna()
        if len(non_null_values) == 0:
            return []
        
        sample_size = min(n, len(non_null_values))
        return non_null_values.head(sample_size).tolist()
    
    def _analyze_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze numeric column statistics."""
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        return {
            'min_value': numeric_series.min(),
            'max_value': numeric_series.max(),
            'mean_value': numeric_series.mean(),
            'median_value': numeric_series.median(),
            'std_deviation': numeric_series.std()
        }
    
    def _analyze_text_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze text column characteristics."""
        text_series = series.astype(str)
        
        # Calculate text lengths
        lengths = text_series.str.len()
        
        # Detect potential languages (basic heuristic)
        languages = self._detect_languages(text_series)
        
        return {
            'avg_length': lengths.mean(),
            'min_length': lengths.min(),
            'max_length': lengths.max(),
            'potential_languages': languages,
            'contains_non_ascii': any(not text.isascii() for text in text_series.dropna())
        }
    
    def _analyze_datetime_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze datetime column characteristics."""
        try:
            # Try to convert to datetime
            dt_series = pd.to_datetime(series, errors='coerce')
            
            return {
                'min_date': dt_series.min(),
                'max_date': dt_series.max(),
                'date_range_days': (dt_series.max() - dt_series.min()).days if dt_series.max() and dt_series.min() else None
            }
        except:
            return {}
    
    def _detect_languages(self, text_series: pd.Series) -> List[str]:
        """Basic language detection based on character patterns."""
        languages = set()
        
        sample_text = ' '.join(text_series.dropna().head(10).astype(str))
        
        # Simple heuristics for common languages
        if re.search(r'[áéíóúñü]', sample_text, re.IGNORECASE):
            languages.add('Spanish')
        if re.search(r'[àâäçéèêëïîôùûüÿ]', sample_text, re.IGNORECASE):
            languages.add('French')
        if re.search(r'[äöüß]', sample_text, re.IGNORECASE):
            languages.add('German')
        if re.search(r'[àèéìíîòóù]', sample_text, re.IGNORECASE):
            languages.add('Italian')
        if re.search(r'[ãâáàçéêíôõú]', sample_text, re.IGNORECASE):
            languages.add('Portuguese')
        if re.search(r'[а-яё]', sample_text, re.IGNORECASE):
            languages.add('Russian')
        if re.search(r'[一-龯]', sample_text):
            languages.add('Chinese')
        if re.search(r'[ひらがなカタカナ]', sample_text):
            languages.add('Japanese')
        if re.search(r'[가-힣]', sample_text):
            languages.add('Korean')
        
        return list(languages) if languages else ['English']
    
    def _get_memory_usage(self, df: pd.DataFrame) -> str:
        """Get memory usage of the DataFrame."""
        memory_bytes = df.memory_usage(deep=True).sum()
        
        if memory_bytes < 1024:
            return f"{memory_bytes} bytes"
        elif memory_bytes < 1024 * 1024:
            return f"{memory_bytes / 1024:.1f} KB"
        else:
            return f"{memory_bytes / (1024 * 1024):.1f} MB"
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a text report of the analysis."""
        report = []
        report.append("CSV DATA ANALYSIS REPORT")
        report.append("=" * 30)
        report.append(f"Total Rows: {analysis['total_rows']}")
        report.append(f"Total Columns: {analysis['total_columns']}")
        report.append(f"Memory Usage: {analysis['memory_usage']}")
        report.append(f"Missing Values: {analysis['total_missing_values']}")
        report.append("")
        
        report.append("COLUMN BREAKDOWN:")
        report.append("-" * 20)
        report.append(f"Text Columns: {len(analysis['text_columns'])}")
        for col in analysis['text_columns']:
            report.append(f"  - {col}")
        
        report.append(f"Numeric Columns: {len(analysis['numeric_columns'])}")
        for col in analysis['numeric_columns']:
            report.append(f"  - {col}")
        
        report.append(f"Date Columns: {len(analysis['date_columns'])}")
        for col in analysis['date_columns']:
            report.append(f"  - {col}")
        
        report.append("")
        report.append("DETAILED COLUMN ANALYSIS:")
        report.append("-" * 30)
        
        for col_name, col_info in analysis['columns'].items():
            report.append(f"\nColumn: {col_name}")
            report.append(f"  Type: {col_info['type']}")
            report.append(f"  Non-null Count: {col_info['non_null_count']}")
            report.append(f"  Null Count: {col_info['null_count']}")
            report.append(f"  Unique Count: {col_info['unique_count']}")
            report.append(f"  Sample Values: {col_info['sample_values']}")
        
        return "\n".join(report)
