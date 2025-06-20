import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.csv_analyzer import CSVAnalyzer
from utils.translator import TextTranslator
from utils.visualizer import DataVisualizer
import io

# Configure page
st.set_page_config(
    page_title="CSV Data Analyzer & Translator",
    page_icon="🌸",
    layout="wide"
)

# Custom CSS for beautiful pink/rose theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #ffeef8 0%, #fff0f5 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #ffeef8 0%, #fff0f5 100%);
    }
    
    .stHeader {
        background: rgba(255, 182, 193, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .stMetric {
        background: rgba(255, 192, 203, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid rgba(255, 182, 193, 0.2);
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 228, 225, 0.3);
        border-radius: 5px;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ff69b4, #ff1493);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff1493, #dc143c);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.3);
    }
    
    .stMarkdown h1 {
        color: #d63384;
        text-shadow: 2px 2px 4px rgba(255, 182, 193, 0.3);
    }
    
    .stMarkdown h2 {
        color: #c2185b;
        text-shadow: 1px 1px 2px rgba(255, 182, 193, 0.2);
    }
    
    .stMarkdown h3 {
        color: #ad1457;
    }
    
    .stFileUploader > div {
        background: rgba(255, 228, 225, 0.2);
        border: 2px dashed #ff69b4;
        border-radius: 10px;
        padding: 2rem;
    }
    
    .stSuccess {
        background: rgba(144, 238, 144, 0.1);
        border-left: 4px solid #90ee90;
        border-radius: 5px;
    }
    
    .stInfo {
        background: rgba(255, 182, 193, 0.1);
        border-left: 4px solid #ffb6c1;
        border-radius: 5px;
    }
    
    .feedback-card {
        background: rgba(255, 240, 245, 0.8);
        border: 1px solid rgba(255, 182, 193, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(255, 182, 193, 0.2);
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(45deg, #ffb6c1, #ffc0cb);
        border-radius: 1px;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📊 CSV Data Analyzer & Translator")
    st.markdown("Upload your CSV file to analyze, translate, and visualize your data in a beautiful format!")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'translated_data' not in st.session_state:
        st.session_state.translated_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'column_translations' not in st.session_state:
        st.session_state.column_translations = {}
    
    # File upload section
    st.header("🔄 Upload CSV File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type=['csv'],
        help="Upload a CSV file to analyze and translate its content"
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV with encoding detection
            try:
                # Try UTF-8 first
                content = uploaded_file.read()
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback to other encodings
                uploaded_file.seek(0)
                content = uploaded_file.read()
                for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(io.StringIO(content.decode(encoding)))
                        break
                    except:
                        continue
                else:
                    st.error("Could not decode the CSV file. Please ensure it's properly encoded.")
                    return
            
            st.session_state.data = df
            st.success(f"✅ Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns!")
            
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            

                
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            return
    
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Analyze CSV structure
        st.header("🔍 Data Analysis")
        
        analyzer = CSVAnalyzer()
        analysis = analyzer.analyze_dataframe(df)
        st.session_state.analysis_results = analysis
        
        # Display analysis results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Column Information")
            analysis_df = pd.DataFrame([
                {
                    'Column': col,
                    'Type': info['type'],
                    'Non-null Count': info['non_null_count'],
                    'Null Count': info['null_count'],
                    'Sample Values': ', '.join(map(str, info['sample_values'][:3]))
                }
                for col, info in analysis['columns'].items()
            ])
            st.dataframe(analysis_df, use_container_width=True)
        
        with col2:
            st.subheader("📊 Data Summary")
            st.write(f"**Memory Usage:** {analysis['memory_usage']}")
            st.write(f"**Text Columns:** {len(analysis['text_columns'])}")
            st.write(f"**Numeric Columns:** {len(analysis['numeric_columns'])}")
            st.write(f"**Date Columns:** {len(analysis['date_columns'])}")
            st.write(f"**Missing Values:** {analysis['total_missing_values']}")
        
        # Translation section
        st.header("🌐 Translation")
        
        text_columns = analysis['text_columns']
        if text_columns:
            target_language = st.selectbox(
                "Select target language:",
                ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                format_func=lambda x: {
                    "en": "English", "es": "Spanish", "fr": "French", 
                    "de": "German", "it": "Italian", "pt": "Portuguese",
                    "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese"
                }[x]
            )
            
            if st.button("🔄 Translate Data"):
                with st.spinner("🌸 Translating data..."):
                    translator = TextTranslator()
                    translated_df = translator.translate_dataframe(
                        df.copy(), 
                        text_columns, 
                        target_language
                    )
                    st.session_state.translated_data = translated_df
                    st.success("✅ Translation completed!")
        else:
            st.info("No text columns found for translation.")

        # Display data section
        if st.session_state.translated_data is not None:
            # Beautiful translated data display
            st.header("🌸 Translated Feedback")
            
            # Beautiful card view for translated responses
            card_data = st.session_state.translated_data
            
            for idx, row in card_data.iterrows():
                with st.container():
                    st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
                    st.markdown("### 🌸 Translated Feedback")
                    
                    # Get columns in proper order (timestamp first, then text columns)
                    all_cols = [col for col in st.session_state.translated_data.columns if not col.endswith('_original')]
                    timestamp_cols = [col for col in all_cols if 'timestamp' in col.lower() or 'date' in col.lower() or 'time' in col.lower()]
                    text_cols = [col for col in all_cols if col not in timestamp_cols]
                    ordered_cols = timestamp_cols + text_cols
                    
                    # Display each column with emojis and formatting in order
                    for col_name in ordered_cols:
                        if col_name not in row.index:
                            continue
                        value = row[col_name]
                        
                        # Determine emoji based on column name/content and position
                        if 'timestamp' in col_name.lower() or 'date' in col_name.lower() or 'time' in col_name.lower():
                            emoji = "📅"
                            label = "Response Submitted"
                            st.markdown(f"**{emoji} {label}:** {value}")
                        else:
                            # For non-timestamp columns, the column name is the question and the value is the answer
                            col_name_str = str(col_name).lower()
                            
                            # Check if column name looks like a question (improved detection)
                            if ('?' in col_name or '¿' in col_name or 
                                'question' in col_name_str or 'pregunta' in col_name_str or
                                'texto' in col_name_str or 'text' in col_name_str or
                                'translated' in col_name_str or 'mango' in col_name_str or
                                'estás' in col_name_str or 'estas' in col_name_str or
                                'algo' in col_name_str or 'favor' in col_name_str or
                                'por favor' in col_name_str or 'como' in col_name_str or
                                'cómo' in col_name_str):
                                # Get translated column name if available
                                translated_question = st.session_state.column_translations.get(col_name, col_name)
                                
                                # Handle empty/NaN values
                                if pd.isna(value) or str(value).strip() == '':
                                    answer_display = "No response"
                                else:
                                    answer_display = str(value)
                                
                                # Display both question (from column name) and answer (from value)
                                st.markdown(f"**📝 Question:** {translated_question}")
                                st.markdown(f"**💬 Answer:** {answer_display}")
                            else:
                                # Regular column display
                                emoji = "📄"
                                label = col_name.replace('_', ' ').title()
                                
                                # Handle empty/NaN values
                                if pd.isna(value) or str(value).strip() == '':
                                    value_display = "No response"
                                else:
                                    value_display = str(value)
                                    
                                st.markdown(f"**{emoji} {label}:** {value_display}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Original data display
            st.header("📋 Data Preview")
            
            display_data = df
            
            # Add filtering options
            if len(display_data) > 100:
                show_all = st.checkbox("Show all rows", value=False)
                if not show_all:
                    display_data = display_data.head(100)
                    st.info(f"Showing first 100 rows of {len(df)} total rows")
            
            # Display the data table
            st.dataframe(
                display_data,
                use_container_width=True,
                height=400
            )
        

        
        # Download section
        st.header("💾 Download Results")
        
        if st.session_state.translated_data is not None:
            csv_buffer = io.StringIO()
            st.session_state.translated_data.to_csv(csv_buffer, index=False)
            csv_string = csv_buffer.getvalue()
            
            st.download_button(
                label="📥 Download Translated CSV",
                data=csv_string,
                file_name="translated_data.csv",
                mime="text/csv"
            )
        
        # Analysis report download
        if st.session_state.analysis_results:
            report = analyzer.generate_report(st.session_state.analysis_results)
            st.download_button(
                label="📊 Download Analysis Report",
                data=report,
                file_name="analysis_report.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
