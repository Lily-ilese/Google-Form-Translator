import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any
import re

class DataVisualizer:
    """Creates interactive visualizations for CSV data."""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_histogram(self, df: pd.DataFrame, column: str) -> go.Figure:
        """Create a histogram for a numeric column."""
        try:
            # Convert to numeric, handling any string values
            numeric_data = pd.to_numeric(df[column], errors='coerce').dropna()
            
            if len(numeric_data) == 0:
                # Create empty figure with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No numeric data available for visualization",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title=f"Histogram: {column}")
                return fig
            
            fig = px.histogram(
                x=numeric_data,
                title=f"Distribution of {column}",
                labels={'x': column, 'count': 'Frequency'},
                nbins=min(50, max(10, len(numeric_data) // 10))
            )
            
            # Add statistics annotations
            mean_val = numeric_data.mean()
            median_val = numeric_data.median()
            
            fig.add_vline(
                x=mean_val, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Mean: {mean_val:.2f}"
            )
            
            fig.add_vline(
                x=median_val, 
                line_dash="dot", 
                line_color="blue",
                annotation_text=f"Median: {median_val:.2f}"
            )
            
            fig.update_layout(
                showlegend=True,
                height=400
            )
            
            return fig
            
        except Exception as e:
            # Create error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating histogram: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"Histogram: {column}")
            return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create a correlation heatmap for numeric columns."""
        try:
            # Select only numeric columns and calculate correlation
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty or len(numeric_df.columns) < 2:
                fig = go.Figure()
                fig.add_annotation(
                    text="Need at least 2 numeric columns for correlation analysis",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title="Correlation Matrix")
                return fig
            
            correlation_matrix = numeric_df.corr()
            
            fig = px.imshow(
                correlation_matrix,
                title="Correlation Matrix",
                color_continuous_scale='RdBu',
                aspect='auto',
                text_auto=True
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating correlation heatmap: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title="Correlation Matrix")
            return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
        """Create a scatter plot between two numeric columns."""
        try:
            # Prepare data
            plot_data = df[[x_col, y_col]].copy()
            if color_col and color_col in df.columns:
                plot_data[color_col] = df[color_col]
            
            # Remove rows with NaN values
            plot_data = plot_data.dropna()
            
            if plot_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No valid data points for scatter plot",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title=f"Scatter: {x_col} vs {y_col}")
                return fig
            
            fig = px.scatter(
                plot_data,
                x=x_col,
                y=y_col,
                color=color_col if color_col else None,
                title=f"{x_col} vs {y_col}",
                trendline="ols" if len(plot_data) > 10 else None
            )
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating scatter plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"Scatter: {x_col} vs {y_col}")
            return fig
    
    def create_box_plot(self, df: pd.DataFrame, column: str, group_by: str = None) -> go.Figure:
        """Create a box plot for a numeric column."""
        try:
            numeric_data = pd.to_numeric(df[column], errors='coerce')
            valid_data = df[numeric_data.notna()].copy()
            valid_data[column] = numeric_data[numeric_data.notna()]
            
            if valid_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No valid numeric data for box plot",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title=f"Box Plot: {column}")
                return fig
            
            if group_by and group_by in df.columns:
                fig = px.box(
                    valid_data,
                    y=column,
                    x=group_by,
                    title=f"Box Plot: {column} by {group_by}"
                )
            else:
                fig = px.box(
                    valid_data,
                    y=column,
                    title=f"Box Plot: {column}"
                )
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating box plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"Box Plot: {column}")
            return fig
    
    def analyze_text_length(self, df: pd.DataFrame, column: str) -> pd.Series:
        """Analyze text lengths in a column."""
        try:
            text_data = df[column].astype(str)
            lengths = text_data.str.len()
            return lengths
        except Exception:
            return pd.Series(dtype=int)
    
    def create_text_length_chart(self, lengths: pd.Series, column_name: str) -> go.Figure:
        """Create a chart showing text length distribution."""
        try:
            if lengths.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No text data available for analysis",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title=f"Text Length Analysis: {column_name}")
                return fig
            
            fig = px.histogram(
                x=lengths,
                title=f"Text Length Distribution: {column_name}",
                labels={'x': 'Text Length (characters)', 'count': 'Frequency'},
                nbins=min(30, max(10, len(lengths) // 20))
            )
            
            # Add statistics
            mean_length = lengths.mean()
            median_length = lengths.median()
            
            fig.add_vline(
                x=mean_length,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {mean_length:.1f}"
            )
            
            fig.add_vline(
                x=median_length,
                line_dash="dot",
                line_color="blue",
                annotation_text=f"Median: {median_length:.1f}"
            )
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating text length chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"Text Length Analysis: {column_name}")
            return fig
    
    def create_value_counts_chart(self, df: pd.DataFrame, column: str, top_n: int = 10) -> go.Figure:
        """Create a bar chart showing value counts for a categorical column."""
        try:
            value_counts = df[column].value_counts().head(top_n)
            
            if value_counts.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available for value counts",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title=f"Value Counts: {column}")
                return fig
            
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Top {len(value_counts)} Values: {column}",
                labels={'x': column, 'y': 'Count'}
            )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating value counts chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"Value Counts: {column}")
            return fig
    
    def create_time_series_plot(self, df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
        """Create a time series plot."""
        try:
            # Prepare data
            plot_data = df[[date_col, value_col]].copy()
            plot_data[date_col] = pd.to_datetime(plot_data[date_col], errors='coerce')
            plot_data[value_col] = pd.to_numeric(plot_data[value_col], errors='coerce')
            
            # Remove invalid data
            plot_data = plot_data.dropna()
            
            if plot_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No valid time series data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title=f"Time Series: {value_col} over {date_col}")
                return fig
            
            # Sort by date
            plot_data = plot_data.sort_values(date_col)
            
            fig = px.line(
                plot_data,
                x=date_col,
                y=value_col,
                title=f"Time Series: {value_col} over {date_col}",
                markers=True
            )
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating time series plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"Time Series: {value_col} over {date_col}")
            return fig
