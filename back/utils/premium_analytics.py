# utils/premium_analytics.py
"""
Premium analytics utility for wagtee SaaS platform
Integrates Plotly, pandas, and numpy with Django for advanced business analytics
Following Django and Context7 best practices for performance and scalability
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import plot
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.core.cache import cache
import hashlib
import logging

logger = logging.getLogger(__name__)


class PremiumAnalytics:
    """
    Advanced analytics engine for wagtee SaaS platform
    Provides premium Plotly visualizations with Django integration
    """
    
    # Color schemes for consistent branding
    COLORS = {
        'primary': '#6366F1',  # Indigo
        'secondary': '#EC4899',  # Pink
        'success': '#10B981',  # Emerald
        'warning': '#F59E0B',  # Amber
        'danger': '#EF4444',   # Red
        'info': '#06B6D4',     # Cyan
        'dark': '#374151',     # Gray-700
        'light': '#F9FAFB',    # Gray-50
    }
    
    SAUDI_COLORS = [
        '#006C35',  # Saudi Green
        '#FFD700',  # Gold
        '#8B4513',  # Brown
        '#4169E1',  # Royal Blue
        '#DC143C',  # Crimson
        '#FF6347',  # Tomato
        '#32CD32',  # Lime Green
        '#FF1493',  # Deep Pink
    ]
    
    @classmethod
    def _get_cache_key(cls, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"analytics:{prefix}:{hash_key}"
    
    @classmethod
    def _cache_chart(cls, key: str, chart_html: str, timeout: int = 3600):
        """Cache chart HTML with timeout"""
        cache.set(key, chart_html, timeout)
    
    @classmethod
    def _get_cached_chart(cls, key: str) -> str:
        """Retrieve cached chart HTML"""
        return cache.get(key)
    
    @classmethod
    def prepare_dataframe(cls, queryset, date_field='created_at', value_field=None):
        """
        Convert Django queryset to optimized pandas DataFrame
        Following pandas best practices for database integration
        """
        try:
            # Use values() for efficient database query
            values_list = list(queryset.values())
            
            if not values_list:
                return pd.DataFrame()
            
            # Create DataFrame with optimized dtypes
            df = pd.DataFrame(values_list)
            
            # Optimize datetime columns
            if date_field in df.columns:
                df[date_field] = pd.to_datetime(df[date_field])
                # Set timezone-aware datetime for Saudi timezone
                df[date_field] = df[date_field].dt.tz_convert('Asia/Riyadh')
            
            # Optimize numeric columns using pandas downcast
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if col != value_field:  # Preserve precision for main value field
                    df[col] = pd.to_numeric(df[col], downcast='integer')
            
            # Optimize categorical columns
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.5:  # High repetition
                    df[col] = df[col].astype('category')
            
            return df
            
        except Exception as e:
            logger.error(f"DataFrame preparation error: {str(e)}")
            return pd.DataFrame()
    
    @classmethod
    def generate_revenue_chart(cls, revenue_data, period='month', **kwargs):
        """
        Generate interactive revenue trend chart
        Following Plotly best practices for Django integration
        """
        cache_key = cls._get_cache_key('revenue_chart', period=period, **kwargs)
        cached_chart = cls._get_cached_chart(cache_key)
        
        if cached_chart:
            return cached_chart
        
        try:
            if not revenue_data:
                return cls._generate_no_data_chart("No revenue data available")
            
            # Prepare DataFrame
            df = pd.DataFrame(revenue_data)
            if df.empty:
                return cls._generate_no_data_chart("No revenue data to display")
            
            # Ensure proper datetime handling
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            elif 'period' in df.columns:
                df['period'] = pd.to_datetime(df['period'])
                df = df.rename(columns={'period': 'date'})
            
            # Sort by date
            df = df.sort_values('date')
            
            # Format revenue values
            df['revenue_formatted'] = df['revenue'].apply(lambda x: f"{x:,.0f} SAR")
            
            # Create interactive line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(
                    color=cls.COLORS['primary'],
                    width=3,
                    shape='spline'  # Smooth line
                ),
                marker=dict(
                    size=8,
                    color=cls.COLORS['primary'],
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{x}</b><br>' +
                             'Revenue: %{customdata}<br>' +
                             '<extra></extra>',
                customdata=df['revenue_formatted']
            ))
            
            # Add trend line
            if len(df) > 2:
                z = np.polyfit(range(len(df)), df['revenue'], 1)
                trend_line = np.poly1d(z)(range(len(df)))
                
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=trend_line,
                    mode='lines',
                    name='Trend',
                    line=dict(
                        color=cls.COLORS['secondary'],
                        width=2,
                        dash='dash'
                    ),
                    opacity=0.7,
                    hoverinfo='skip'
                ))
            
            # Update layout with premium styling
            fig.update_layout(
                title={
                    'text': f'Revenue Trend - {period.title()}',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 24, 'family': 'Arial Black'}
                },
                xaxis_title='Date',
                yaxis_title='Revenue (SAR)',
                font=dict(family="Arial", size=14),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    x=0.02,
                    y=0.98,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='rgba(0,0,0,0.2)',
                    borderwidth=1
                ),
                margin=dict(l=80, r=80, t=80, b=80),
                height=400
            )
            
            # Format axes
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.1)',
                showline=True,
                linewidth=1,
                linecolor='rgba(0,0,0,0.2)'
            )
            
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.1)',
                showline=True,
                linewidth=1,
                linecolor='rgba(0,0,0,0.2)',
                tickformat=',.0f'
            )
            
            # Generate HTML with Django integration
            config = {
                'displayModeBar': True,
                'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                'modeBarButtonsToRemove': ['autoScale2d', 'hoverCompareCartesian'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'revenue_chart_{period}',
                    'height': 600,
                    'width': 1200,
                    'scale': 2
                }
            }
            
            chart_html = plot(fig, output_type='div', include_plotlyjs=True, config=config)
            
            # Cache the result
            cls._cache_chart(cache_key, chart_html)
            
            return chart_html
            
        except Exception as e:
            logger.error(f"Revenue chart generation error: {str(e)}")
            return cls._generate_error_chart(f"Error generating revenue chart: {str(e)}")
    
    @classmethod
    def generate_service_performance_chart(cls, service_data, **kwargs):
        """
        Generate service performance comparison chart
        """
        cache_key = cls._get_cache_key('service_performance', **kwargs)
        cached_chart = cls._get_cached_chart(cache_key)
        
        if cached_chart:
            return cached_chart
        
        try:
            if not service_data:
                return cls._generate_no_data_chart("No service data available")
            
            # Prepare DataFrame
            df = pd.DataFrame(service_data)
            if df.empty:
                return cls._generate_no_data_chart("No service data to display")
            
            # Sort by revenue for better visualization
            df = df.sort_values('revenue', ascending=True)
            
            # Format data
            df['revenue_formatted'] = df['revenue'].apply(lambda x: f"{x:,.0f} SAR")
            df['bookings_formatted'] = df['bookings'].apply(lambda x: f"{x:,} bookings")
            
            # Create horizontal bar chart for better readability with Arabic service names
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=df['service__name'],
                x=df['revenue'],
                name='Revenue',
                orientation='h',
                marker=dict(
                    color=df['revenue'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(
                        title="Revenue (SAR)",
                        titleside="right",
                        tickformat=",.0f"
                    )
                ),
                text=df['revenue_formatted'],
                textposition='inside',
                textfont=dict(color='white', size=12),
                hovertemplate='<b>%{y}</b><br>' +
                             'Revenue: %{customdata[0]}<br>' +
                             'Bookings: %{customdata[1]}<br>' +
                             'Avg Rating: %{customdata[2]:.1f}/5<br>' +
                             '<extra></extra>',
                customdata=np.column_stack((
                    df['revenue_formatted'],
                    df['bookings_formatted'],
                    df.get('avg_rating', [0] * len(df))
                ))
            ))
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Service Performance Analysis',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 24, 'family': 'Arial Black'}
                },
                xaxis_title='Revenue (SAR)',
                yaxis_title='Service',
                font=dict(family="Arial", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=200, r=100, t=80, b=80),
                height=max(400, len(df) * 30 + 100)  # Dynamic height based on data
            )
            
            # Format axes
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat=',.0f'
            )
            
            fig.update_yaxes(
                showgrid=False,
                tickmode='linear'
            )
            
            # Generate HTML
            config = {
                'displayModeBar': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'service_performance_chart',
                    'height': max(600, len(df) * 40 + 150),
                    'width': 1200,
                    'scale': 2
                }
            }
            
            chart_html = plot(fig, output_type='div', include_plotlyjs=True, config=config)
            
            # Cache the result
            cls._cache_chart(cache_key, chart_html)
            
            return chart_html
            
        except Exception as e:
            logger.error(f"Service performance chart error: {str(e)}")
            return cls._generate_error_chart(f"Error generating service performance chart: {str(e)}")
    
    @classmethod
    def generate_activity_heatmap(cls, booking_data, period='week', **kwargs):
        """
        Generate booking activity heatmap
        """
        cache_key = cls._get_cache_key('activity_heatmap', period=period, **kwargs)
        cached_chart = cls._get_cached_chart(cache_key)
        
        if cached_chart:
            return cached_chart
        
        try:
            if not booking_data:
                return cls._generate_no_data_chart("No booking data available")
            
            # Prepare DataFrame
            df = pd.DataFrame(booking_data)
            if df.empty:
                return cls._generate_no_data_chart("No booking data to display")
            
            # Convert datetime
            df['appointment_date'] = pd.to_datetime(df['appointment_date'])
            df['hour'] = pd.to_datetime(df['appointment_time'], format='%H:%M:%S').dt.hour
            df['day_of_week'] = df['appointment_date'].dt.day_name()
            
            # Create pivot table for heatmap
            heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='bookings')
            heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='bookings')
            
            # Reorder days (Saudi week starts Saturday)
            day_order = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            heatmap_pivot = heatmap_pivot.reindex(day_order)
            heatmap_pivot = heatmap_pivot.fillna(0)
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_pivot.values,
                x=[f'{h:02d}:00' for h in heatmap_pivot.columns],
                y=heatmap_pivot.index,
                colorscale=[
                    [0, 'rgba(255,255,255,0.1)'],
                    [0.2, '#E0F2FE'],
                    [0.4, '#7DD3FC'],
                    [0.6, '#0EA5E9'],
                    [0.8, '#0284C7'],
                    [1.0, '#0C4A6E']
                ],
                hoverongaps=False,
                hovertemplate='<b>%{y}</b><br>' +
                             'Time: %{x}<br>' +
                             'Bookings: %{z}<br>' +
                             '<extra></extra>',
                colorbar=dict(
                    title="Number of Bookings",
                    titleside="right",
                    tickmode="linear",
                    tick0=0,
                    dtick=max(1, int(heatmap_pivot.values.max() / 10))
                )
            ))
            
            # Update layout
            fig.update_layout(
                title={
                    'text': f'Booking Activity Heatmap - {period.title()}',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Arial Black'}
                },
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week',
                font=dict(family="Arial", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                margin=dict(l=100, r=150, t=80, b=80)
            )
            
            # Update axes
            fig.update_xaxes(
                side='bottom',
                tickangle=0
            )
            
            fig.update_yaxes(
                side='left'
            )
            
            # Generate HTML
            config = {
                'displayModeBar': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'activity_heatmap_{period}',
                    'height': 600,
                    'width': 1200,
                    'scale': 2
                }
            }
            
            chart_html = plot(fig, output_type='div', include_plotlyjs=True, config=config)
            
            # Cache the result
            cls._cache_chart(cache_key, chart_html)
            
            return chart_html
            
        except Exception as e:
            logger.error(f"Activity heatmap error: {str(e)}")
            return cls._generate_error_chart(f"Error generating activity heatmap: {str(e)}")
    
    @classmethod
    def generate_customer_segment_chart(cls, customer_data, **kwargs):
        """
        Generate customer segmentation pie chart
        """
        cache_key = cls._get_cache_key('customer_segments', **kwargs)
        cached_chart = cls._get_cached_chart(cache_key)
        
        if cached_chart:
            return cached_chart
        
        try:
            if not customer_data:
                return cls._generate_no_data_chart("No customer data available")
            
            # Prepare customer segmentation
            segments = {
                'New Customers (1 booking)': 0,
                'Regular Customers (2-5 bookings)': 0,
                'Loyal Customers (6-10 bookings)': 0,
                'VIP Customers (11+ bookings)': 0
            }
            
            # Segment customers based on booking count
            for customer in customer_data:
                booking_count = customer.get('total_bookings', 0)
                if booking_count == 1:
                    segments['New Customers (1 booking)'] += 1
                elif 2 <= booking_count <= 5:
                    segments['Regular Customers (2-5 bookings)'] += 1
                elif 6 <= booking_count <= 10:
                    segments['Loyal Customers (6-10 bookings)'] += 1
                else:
                    segments['VIP Customers (11+ bookings)'] += 1
            
            # Filter out empty segments
            segments = {k: v for k, v in segments.items() if v > 0}
            
            if not segments:
                return cls._generate_no_data_chart("No customer segmentation data available")
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(segments.keys()),
                values=list(segments.values()),
                hole=0.4,  # Donut style
                marker=dict(
                    colors=cls.SAUDI_COLORS[:len(segments)],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>' +
                             'Count: %{value}<br>' +
                             'Percentage: %{percent}<br>' +
                             '<extra></extra>',
                pull=[0.05 if 'VIP' in label else 0 for label in segments.keys()]  # Highlight VIP
            )])
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Customer Segmentation',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 24, 'family': 'Arial Black'}
                },
                font=dict(family="Arial", size=14),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(
                    orientation="v",
                    x=1.05,
                    y=0.5,
                    xanchor="left",
                    yanchor="middle"
                ),
                margin=dict(l=80, r=200, t=80, b=80),
                height=500,
                annotations=[dict(
                    text=f'Total<br>Customers<br><b>{sum(segments.values())}</b>',
                    x=0.5, y=0.5,
                    font_size=16,
                    showarrow=False
                )]
            )
            
            # Generate HTML
            config = {
                'displayModeBar': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'customer_segmentation_chart',
                    'height': 600,
                    'width': 1200,
                    'scale': 2
                }
            }
            
            chart_html = plot(fig, output_type='div', include_plotlyjs=True, config=config)
            
            # Cache the result
            cls._cache_chart(cache_key, chart_html)
            
            return chart_html
            
        except Exception as e:
            logger.error(f"Customer segment chart error: {str(e)}")
            return cls._generate_error_chart(f"Error generating customer segment chart: {str(e)}")
    
    @classmethod
    def generate_growth_metrics(cls, current_data, previous_data):
        """
        Calculate growth metrics comparing current and previous periods
        """
        try:
            if not current_data or not previous_data:
                return {
                    'revenue_growth': 0,
                    'booking_growth': 0,
                    'customer_growth': 0,
                    'average_order_growth': 0
                }
            
            # Calculate totals
            current_revenue = sum(item.get('revenue', 0) for item in current_data)
            previous_revenue = sum(item.get('revenue', 0) for item in previous_data)
            
            current_bookings = sum(item.get('bookings', 0) for item in current_data)
            previous_bookings = sum(item.get('bookings', 0) for item in previous_data)
            
            # Calculate growth percentages
            def calculate_growth(current, previous):
                if previous == 0:
                    return 100 if current > 0 else 0
                return ((current - previous) / previous) * 100
            
            revenue_growth = calculate_growth(current_revenue, previous_revenue)
            booking_growth = calculate_growth(current_bookings, previous_bookings)
            
            # Average order value growth
            current_aov = current_revenue / current_bookings if current_bookings > 0 else 0
            previous_aov = previous_revenue / previous_bookings if previous_bookings > 0 else 0
            aov_growth = calculate_growth(current_aov, previous_aov)
            
            return {
                'revenue_growth': round(revenue_growth, 2),
                'booking_growth': round(booking_growth, 2),
                'average_order_growth': round(aov_growth, 2),
                'current_revenue': current_revenue,
                'previous_revenue': previous_revenue,
                'current_bookings': current_bookings,
                'previous_bookings': previous_bookings
            }
            
        except Exception as e:
            logger.error(f"Growth metrics calculation error: {str(e)}")
            return {
                'revenue_growth': 0,
                'booking_growth': 0,
                'customer_growth': 0,
                'average_order_growth': 0
            }
    
    @classmethod
    def _generate_no_data_chart(cls, message: str) -> str:
        """Generate a chart indicating no data available"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        return plot(fig, output_type='div', include_plotlyjs=True)
    
    @classmethod
    def _generate_error_chart(cls, error_message: str) -> str:
        """Generate a chart indicating an error occurred"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ {error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        return plot(fig, output_type='div', include_plotlyjs=True)


class BusinessIntelligence:
    """
    Business Intelligence helper class
    Provides advanced analytics calculations using pandas and numpy
    """
    
    @classmethod
    def calculate_customer_lifetime_value(cls, customer_data):
        """Calculate Customer Lifetime Value using pandas"""
        try:
            if not customer_data:
                return 0
            
            df = pd.DataFrame(customer_data)
            if df.empty:
                return 0
            
            # Calculate average order value and purchase frequency
            avg_order_value = df['total_spent'].mean()
            avg_purchase_frequency = df['total_bookings'].mean()
            
            # Estimate customer lifespan (in months) based on data
            if 'first_booking_date' in df.columns:
                df['first_booking_date'] = pd.to_datetime(df['first_booking_date'])
                customer_age_days = (timezone.now().date() - df['first_booking_date'].dt.date).dt.days
                avg_customer_lifespan_months = customer_age_days.mean() / 30.44
            else:
                avg_customer_lifespan_months = 12  # Default assumption
            
            # CLV = AOV × Purchase Frequency × Customer Lifespan
            clv = avg_order_value * avg_purchase_frequency * avg_customer_lifespan_months
            
            return round(clv, 2)
            
        except Exception as e:
            logger.error(f"CLV calculation error: {str(e)}")
            return 0
    
    @classmethod
    def calculate_customer_acquisition_cost(cls, marketing_spend, new_customers):
        """Calculate Customer Acquisition Cost"""
        try:
            if new_customers == 0:
                return 0
            return round(marketing_spend / new_customers, 2)
        except:
            return 0
    
    @classmethod
    def analyze_booking_patterns(cls, booking_data):
        """Analyze booking patterns using pandas"""
        try:
            if not booking_data:
                return {}
            
            df = pd.DataFrame(booking_data)
            if df.empty:
                return {}
            
            df['appointment_date'] = pd.to_datetime(df['appointment_date'])
            df['hour'] = pd.to_datetime(df['appointment_time'], format='%H:%M:%S').dt.hour
            df['day_of_week'] = df['appointment_date'].dt.day_name()
            df['month'] = df['appointment_date'].dt.month
            
            patterns = {
                'peak_hours': df.groupby('hour').size().idxmax(),
                'peak_day': df.groupby('day_of_week').size().idxmax(),
                'peak_month': df.groupby('month').size().idxmax(),
                'hourly_distribution': df.groupby('hour').size().to_dict(),
                'daily_distribution': df.groupby('day_of_week').size().to_dict(),
                'seasonal_trends': df.groupby('month').size().to_dict()
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Booking patterns analysis error: {str(e)}")
            return {}
    
    @classmethod
    def calculate_service_profitability(cls, service_data, overhead_percentage=0.3):
        """Calculate service profitability analysis"""
        try:
            if not service_data:
                return []
            
            df = pd.DataFrame(service_data)
            if df.empty:
                return []
            
            # Calculate profit margins
            df['overhead_cost'] = df['revenue'] * overhead_percentage
            df['profit'] = df['revenue'] - df['overhead_cost']
            df['profit_margin'] = (df['profit'] / df['revenue'] * 100).round(2)
            
            # Sort by profitability
            df = df.sort_values('profit_margin', ascending=False)
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Service profitability calculation error: {str(e)}")
            return []