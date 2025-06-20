import pandas as pd
import os
from typing import List, Dict, Any
import time
import streamlit as st

# Try to import Google Translate, fallback to mock translation if not available
try:
    from googletrans import Translator, LANGUAGES
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

class TextTranslator:
    """Handles text translation using Google Translate API."""
    
    def __init__(self):
        self.translator = None
        self.api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY", None)
        
        if GOOGLE_TRANSLATE_AVAILABLE:
            try:
                self.translator = Translator()
                # Test the translator
                self.translator.translate("test", dest='en')
            except Exception as e:
                st.warning(f"Google Translate initialization failed: {str(e)}")
                self.translator = None
    
    def translate_text(self, text: str, target_language: str = 'en', source_language: str = 'auto') -> str:
        """Translate a single text string."""
        if not text or pd.isna(text):
            return text
        
        text_str = str(text).strip()
        if not text_str:
            return text
        
        # Skip translation if text is too short or looks like it's already in target language
        if len(text_str) < 3:
            return text
        
        try:
            if self.translator and GOOGLE_TRANSLATE_AVAILABLE:
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
                result = self.translator.translate(
                    text_str, 
                    dest=target_language, 
                    src=source_language
                )
                
                return result.text if result and hasattr(result, 'text') else text_str
            else:
                # Fallback: return original text with indication
                return f"[Translation unavailable] {text_str}"
                
        except Exception as e:
            st.warning(f"Translation failed for text '{text_str[:50]}...': {str(e)}")
            return text_str
    
    def translate_dataframe(self, df: pd.DataFrame, columns: List[str], target_language: str = 'en') -> pd.DataFrame:
        """Translate specified columns in a DataFrame."""
        if not columns:
            return df
        
        translated_df = df.copy()
        
        # Create progress bar
        total_cells = sum(len(df[col].dropna()) for col in columns if col in df.columns)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed_cells = 0
        
        # Dictionary to store translated column names
        column_translations = {}
        
        for column in columns:
            if column not in df.columns:
                st.warning(f"Column '{column}' not found in DataFrame")
                continue
            
            status_text.text(f"Translating column: {column}")
            
            # Translate column name if it contains question markers (improved detection)
            col_lower = column.lower()
            if ('?' in column or '¿' in column or 
                'texto' in col_lower or 'text' in col_lower or
                'translated' in col_lower or 'mango' in col_lower or
                'estás' in col_lower or 'estas' in col_lower or
                'algo' in col_lower or 'favor' in col_lower or
                'por favor' in col_lower or 'como' in col_lower or
                'cómo' in col_lower):
                translated_column_name = self.translate_text(column, target_language)
                column_translations[column] = translated_column_name
            
            # Get non-null values
            non_null_mask = df[column].notna()
            non_null_values = df.loc[non_null_mask, column]
            
            translated_values = []
            
            for i, value in enumerate(non_null_values):
                # Only translate non-empty values
                if pd.isna(value) or str(value).strip() == '':
                    translated_values.append(value)
                else:
                    translated_text = self.translate_text(value, target_language)
                    translated_values.append(translated_text)
                
                processed_cells += 1
                if processed_cells % 5 == 0:  # Update progress every 5 cells
                    progress = min(processed_cells / total_cells, 1.0)
                    progress_bar.progress(progress)
            
            # Update the DataFrame with translated values
            translated_df.loc[non_null_mask, column] = translated_values
            
            # Create a new column with original values for comparison
            original_column_name = f"{column}_original"
            if original_column_name not in translated_df.columns:
                translated_df[original_column_name] = df[column]
        
        # Store column translations for later use
        if hasattr(st.session_state, 'column_translations'):
            st.session_state.column_translations.update(column_translations)
        else:
            st.session_state.column_translations = column_translations
        
        progress_bar.progress(1.0)
        status_text.text("Translation completed!")
        
        # Clear progress indicators after a short delay
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return translated_df
    
    def detect_language(self, text: str) -> str:
        """Detect the language of a text string."""
        if not text or pd.isna(text):
            return 'unknown'
        
        text_str = str(text).strip()
        if not text_str:
            return 'unknown'
        
        try:
            if self.translator and GOOGLE_TRANSLATE_AVAILABLE:
                detected = self.translator.detect(text_str)
                return detected.lang if detected and hasattr(detected, 'lang') else 'unknown'
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names."""
        if GOOGLE_TRANSLATE_AVAILABLE:
            return LANGUAGES
        else:
            # Fallback language list
            return {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'ja': 'Japanese',
                'ko': 'Korean',
                'zh': 'Chinese'
            }
    
    def batch_translate(self, texts: List[str], target_language: str = 'en', batch_size: int = 10) -> List[str]:
        """Translate a batch of texts efficiently."""
        if not texts:
            return []
        
        translated_texts = []
        
        # Process in batches to avoid rate limiting
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                translated = self.translate_text(text, target_language)
                batch_results.append(translated)
                
                # Small delay between translations
                time.sleep(0.1)
            
            translated_texts.extend(batch_results)
        
        return translated_texts
    
    def is_translation_available(self) -> bool:
        """Check if translation service is available."""
        return self.translator is not None and GOOGLE_TRANSLATE_AVAILABLE
    
    def get_translation_info(self) -> str:
        """Get information about translation service status."""
        if self.is_translation_available():
            return "✅ Google Translate service is available"
        elif not GOOGLE_TRANSLATE_AVAILABLE:
            return "⚠️ Google Translate library not installed. Install with: pip install googletrans==4.0.0-rc1"
        else:
            return "❌ Google Translate service initialization failed"
