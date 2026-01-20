"""
Streamlit UI for AI Accounting Mapper
3 tabs: Single Test, Batch Processing, Training Data Management
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import config
from src.mapper import AIMapper
from src.utils import format_confidence, get_method_color, truncate_text
import time


# Page configuration
st.set_page_config(
    page_title="AI Accounting Mapper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional accounting blue theme
st.markdown(f"""
<style>
    :root {{
        --primary-blue: {config.COLORS['primary_blue']};
        --secondary-blue: {config.COLORS['secondary_blue']};
        --bg-light: {config.COLORS['bg_light']};
        --success-green: {config.COLORS['success_green']};
        --warning-amber: {config.COLORS['warning_amber']};
        --danger-red: {config.COLORS['danger_red']};
    }}
    
    .main {{
        background-color: var(--bg-light);
    }}
    
    .stButton>button {{
        background-color: var(--primary-blue);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: var(--secondary-blue);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    .prediction-card {{
        background: black;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }}
    
    .method-badge {{
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        margin: 0.25rem;
    }}
    
    .needs-review {{
        background-color: var(--warning-amber);
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
    }}
    
    .success-badge {{
        background-color: var(--success-green);
    }}
    
    .stat-card {{
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue));
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }}
    
    .stat-label {{
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    h1, h2, h3 {{
        color: var(--primary-blue);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
    }}
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'mapper' not in st.session_state:
    try:
        # Try to get API key from Streamlit secrets first, then config
        api_key = st.secrets.get("OPENAI_API_KEY", config.OPENAI_API_KEY)
        st.session_state.mapper = AIMapper(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing mapper: {e}")
        st.stop()

if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None


# Sidebar - Settings
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Company Domain
    st.subheader("Company Context")
    domain = st.selectbox(
        "Domain",
        options=config.COMPANY_DOMAINS,
        index=0,
        help="Select your company's business domain for better LLM context"
    )
    
    if domain != st.session_state.mapper.domain:
        st.session_state.mapper.update_domain(domain)
        st.success("Domain updated!")
    
    st.divider()
    
    # Thresholds
    st.subheader("Matching Thresholds")
    
    fuzzy_threshold = st.slider(
        "Fuzzy Match",
        min_value=0.70,
        max_value=1.0,
        value=config.THRESHOLDS['fuzzy'],
        step=0.05,
        help="Minimum similarity for fuzzy matching"
    )
    
    semantic_threshold = st.slider(
        "Semantic",
        min_value=0.70,
        max_value=1.0,
        value=config.THRESHOLDS['semantic'],
        step=0.05,
        help="Minimum similarity for semantic matching"
    )
    
    embeddings_threshold = st.slider(
        "Embeddings",
        min_value=0.70,
        max_value=1.0,
        value=config.THRESHOLDS['embeddings'],
        step=0.05,
        help="Minimum similarity for embedding matching"
    )
    
    review_threshold = st.slider(
        "Review Threshold",
        min_value=0.50,
        max_value=1.0,
        value=config.THRESHOLDS['review'],
        step=0.05,
        help="Below this confidence, prediction needs review"
    )
    
    # Update thresholds in config
    config.THRESHOLDS['fuzzy'] = fuzzy_threshold
    config.THRESHOLDS['semantic'] = semantic_threshold
    config.THRESHOLDS['embeddings'] = embeddings_threshold
    config.THRESHOLDS['review'] = review_threshold
    
    st.divider()
    
    # OpenAI API Key (if not in environment)
    if not config.OPENAI_API_KEY:
        st.subheader("🔑 OpenAI API Key")
        api_key_input = st.text_input(
            "Enter API Key",
            type="password",
            help="Your OpenAI API key for LLM classification"
        )
        if api_key_input:
            st.session_state.mapper.llm_matcher.api_key = api_key_input
            st.session_state.mapper.llm_matcher.client.api_key = api_key_input
            st.success("API key updated!")
    
    st.divider()
    
    # Session Statistics
    st.subheader("📊 Session Stats")
    session_stats = st.session_state.mapper.get_session_stats()
    
    st.metric("Predictions Made", session_stats['predictions_made'])
    st.metric("LLM Calls", session_stats['llm_stats']['call_count'])
    st.metric("Needs Review", session_stats['needs_review_count'])
    
    # Method distribution
    if session_stats['predictions_made'] > 0:
        st.write("**Method Distribution:**")
        for method, count in session_stats['method_distribution'].items():
            if count > 0:
                percentage = (count / session_stats['predictions_made']) * 100
                st.write(f"• {method.capitalize()}: {count} ({percentage:.1f}%)")


# Main content
st.title("📊 AI Accounting Mapper")
st.markdown("*Intelligent Financial Statement Classification*")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Single Item Test", "📁 Batch Processing", "💾 Training Data"])


# ==================== TAB 1: SINGLE ITEM TEST ====================
with tab1:
    st.header("Test Single Classification")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        primary_group_input = st.text_input(
            "Enter Primary Group",
            placeholder="e.g., Social Media Advertising",
            help="Enter an accounting line item to classify"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        classify_btn = st.button("🎯 Classify", type="primary", use_container_width=True)
    
    if classify_btn and primary_group_input:
        with st.spinner("Analyzing..."):
            result = st.session_state.mapper.predict_single(
                primary_group_input,
                return_decision_trail=True
            )
            st.session_state.last_prediction = result
    
    # Display result
    if st.session_state.last_prediction:
        result = st.session_state.last_prediction
        
        st.markdown("---")
        
        # Main prediction card
        st.markdown(f"""
        <div class="prediction-card">
            <h3>🎯 Prediction Result</h3>
            <div style="margin: 1rem 0;">
                <h2 style="color: var(--primary-blue); margin: 0.5rem 0;">
                    {result['predicted_fs']}
                </h2>
                <p style="font-size: 1.2rem; color: #666;">
                    Confidence: <strong>{format_confidence(result['confidence'])}</strong>
                </p>
                <span class="method-badge" style="background-color: {get_method_color(result['method_used'])};">
                    Method: {result['method_used'].upper()}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Warning if needs review
        if result['needs_review']:
            st.warning(f"""
            ⚠️ **Low Confidence - Needs Review**  
            Alternative suggestion: **{result['low_confidence_alternative']}**  
            Please verify this classification manually.
            """)
        
        # All 12 Classification Columns
        st.markdown("---")
        st.subheader("📊 Complete Classification")
        
        # Balance Sheet Classifications (if applicable)
        if result.get('predicted_fs') == "Balance Sheet":
            with st.expander("📑 Balance Sheet Classifications", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Main Category:**")
                    st.info(result.get('bs_main_category', 'N/A'))
                    
                    st.write("**Classification:**")
                    st.info(result.get('bs_classification', 'N/A'))
                
                with col2:
                    st.write("**Sub-Classification:**")
                    st.info(result.get('bs_sub_classification', 'N/A'))
                    
                    st.write("**Sub-Classification 2:**")
                    st.info(result.get('bs_sub_classification_2', 'N/A'))
        
        # Profit & Loss Classifications (if applicable)
        if result.get('predicted_fs') == "Profit & Loss":
            with st.expander("📈 Profit & Loss Classifications", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Classification:**")
                    st.info(result.get('pl_classification', 'N/A'))
                    
                    st.write("**Sub-Classification:**")
                    st.info(result.get('pl_sub_classification', 'N/A'))
                
                with col2:
                    st.write("**Classification 1:**")
                    st.info(result.get('pl_classification_1', 'N/A'))
        
        # Cash Flow & Expense Type (for both FS types)
        with st.expander("💰 Cash Flow & Expense Classification"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Cash Flow Classification:**")
                st.info(result.get('cf_classification', 'N/A'))
                
                st.write("**Cash Flow Sub-Classification:**")
                st.info(result.get('cf_sub_classification', 'N/A'))
            
            with col2:
                st.write("**Expense Type:**")
                st.info(result.get('expense_type', 'N/A'))
        
        # LLM Reasoning (if applicable)
        if result.get('reasoning'):
            with st.expander("💡 LLM Reasoning"):
                st.write(result['reasoning'])
        
        # Matched Row Details
        if result.get('matched_row_full'):
            with st.expander("📋 Full Matched Training Row"):
                matched_df = pd.DataFrame([result['matched_row_full']])
                st.dataframe(matched_df, use_container_width=True)
        
        # Decision Trail
        if result.get('decision_trail'):
            with st.expander("🔍 Decision Trail (All Methods)"):
                for attempt in result['decision_trail']:
                    method_name = attempt['method'].upper()
                    method_result = attempt['result']
                    
                    if method_result:
                        st.markdown(f"""
                        **{method_name}**: ✅ Match found  
                        - Predicted: {method_result['predicted_fs']}  
                        - Confidence: {format_confidence(method_result['confidence'])}  
                        - Matched: {method_result.get('matched_training_row', 'N/A')}
                        """)
                    else:
                        st.markdown(f"**{method_name}**: ❌ No match")
                    st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add to Training Data", use_container_width=True):
                st.session_state.show_add_modal = True
        
        with col2:
            if st.button("💾 Save Test", use_container_width=True):
                # Save single test
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = config.SINGLE_OUTPUT_DIR / f"single_test_{timestamp}.xlsx"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                df = pd.DataFrame([result])
                df.to_excel(output_file, index=False)
                
                st.success(f"✅ Test saved to: {output_file.name}")
        
        with col3:
            if st.button("🔄 Clear Result", use_container_width=True):
                st.session_state.last_prediction = None
                st.rerun()
    
    # Add to Training Data Modal
    if st.session_state.get('show_add_modal'):
        st.markdown("---")
        st.subheader("➕ Add to Training Data")
        
        with st.form("add_training_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                add_primary_group = st.text_input(
                    "Primary Group",
                    value=st.session_state.last_prediction['primary_group']
                )
            
            with col2:
                add_fs = st.selectbox(
                    "Financial Statement",
                    options=config.VALID_FS_VALUES,
                    index=0 if st.session_state.last_prediction['predicted_fs'] == "Balance Sheet" else 1
                )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Add", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submit:
                add_result = st.session_state.mapper.add_to_training_data(add_primary_group, add_fs)
                if add_result['success']:
                    st.success(add_result['message'])
                    st.session_state.show_add_modal = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(add_result['message'])
            
            if cancel:
                st.session_state.show_add_modal = False
                st.rerun()


# ==================== TAB 2: BATCH PROCESSING ====================
with tab2:
    st.header("Batch Processing")
    
    # Check for incomplete batch
    checkpoint = st.session_state.mapper.check_checkpoint()
    if checkpoint:
        st.warning(f"""
        ⚠️ **Incomplete Batch Found**  
        File: `{Path(checkpoint['input_file']).name}`  
        Processed: {checkpoint['processed_rows']} rows  
        Last updated: {checkpoint['timestamp']}
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Resume", use_container_width=True):
                st.session_state.resume_batch = True
        with col2:
            if st.button("🔄 Start Fresh", use_container_width=True):
                config.PROGRESS_CHECKPOINT.unlink()
                st.session_state.resume_batch = False
                st.rerun()
        
        st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Excel file must contain a 'primary_group' column"
    )
    
    if uploaded_file:
        # Save uploaded file
        input_path = config.INPUT_DIR / uploaded_file.name
        input_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Preview data
        st.subheader("📋 Preview")
        try:
            preview_df = pd.read_excel(input_path)
            
            if 'primary_group' not in preview_df.columns:
                st.error("❌ File must contain 'primary_group' column!")
            else:
                st.info(f"Total rows: {len(preview_df)}")
                st.dataframe(preview_df.head(10), use_container_width=True)
                
                # Process button
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    process_btn = st.button("▶️ Start Processing", type="primary", use_container_width=True)
                
                if process_btn:
                    st.session_state.processing = True
                
                # Processing
                if st.session_state.get('processing'):
                    st.markdown("---")
                    st.subheader("⚙️ Processing...")
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def progress_callback(row_num, total_rows, current_item):
                        progress = row_num / total_rows
                        progress_bar.progress(progress)
                        status_text.text(f"Processing: {row_num}/{total_rows} - {truncate_text(current_item, 40)}")
                    
                    # Run batch processing
                    resume = st.session_state.get('resume_batch', False)
                    result = st.session_state.mapper.predict_batch(
                        input_file=input_path,
                        resume=resume,
                        progress_callback=progress_callback
                    )
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        
                        # Display stats
                        stats = result['stats']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="stat-card">
                                <div class="stat-label">Processed</div>
                                <div class="stat-number">{stats['total_processed']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="stat-card">
                                <div class="stat-label">Needs Review</div>
                                <div class="stat-number">{stats['needs_review_count']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="stat-card">
                                <div class="stat-label">LLM Calls</div>
                                <div class="stat-number">{stats['llm_calls']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col4:
                            st.markdown(f"""
                            <div class="stat-card">
                                <div class="stat-label">Avg Confidence</div>
                                <div class="stat-number">{stats['average_confidence']:.1%}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Method distribution
                        st.subheader("📊 Method Distribution")
                        method_df = pd.DataFrame(
                            list(stats['method_distribution'].items()),
                            columns=['Method', 'Count']
                        )
                        st.bar_chart(method_df.set_index('Method'))
                        
                        # Download button
                        with open(result['output_file'], 'rb') as f:
                            st.download_button(
                                label="📥 Download Results",
                                data=f,
                                file_name=result['output_file'].name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                    else:
                        st.error(f"❌ {result['message']}")
                    
                    st.session_state.processing = False
                    st.session_state.resume_batch = False
        
        except Exception as e:
            st.error(f"Error reading file: {e}")


# ==================== TAB 3: TRAINING DATA MANAGEMENT ====================
with tab3:
    st.header("Training Data Management")
    
    # Stats
    training_stats = st.session_state.mapper.get_training_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", training_stats['total_rows'])
    with col2:
        st.metric("Balance Sheet", training_stats['bs_count'])
    with col3:
        st.metric("Profit & Loss", training_stats['pl_count'])
    with col4:
        st.metric("Last Loaded", training_stats.get('last_loaded', 'Never')[:10] if training_stats.get('last_loaded') else 'Never')
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh from Excel", use_container_width=True):
            with st.spinner("Refreshing..."):
                refresh_result = st.session_state.mapper.refresh_training_data()
                if refresh_result['success']:
                    st.success(f"✅ {refresh_result['message']}")
                    if refresh_result['validation']['warnings']:
                        for warning in refresh_result['validation']['warnings']:
                            st.warning(f"⚠️ {warning}")
                    st.rerun()
                else:
                    st.error(f"❌ {refresh_result['message']}")
    
    with col2:
        if st.button("📥 Download CSV", use_container_width=True):
            csv_path = st.session_state.mapper.data_loader.export_csv()
            if csv_path and csv_path.exists():
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        label="Download training_data.csv",
                        data=f,
                        file_name="training_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.error("Failed to export CSV")
    
    st.markdown("---")
    
    # Search functionality
    st.subheader("🔍 Search Training Data")
    search_query = st.text_input(
        "Search by keyword",
        placeholder="e.g., advertising, salary, inventory"
    )
    
    if search_query:
        search_results = st.session_state.mapper.search_training_data(search_query)
        
        if not search_results.empty:
            st.success(f"Found {len(search_results)} results")
            st.dataframe(search_results, use_container_width=True)
        else:
            st.info("No results found")
    else:
        # Show all training data if no search
        if st.session_state.mapper.data_loader.training_data is not None:
            st.subheader("📊 All Training Data")
            st.dataframe(
                st.session_state.mapper.data_loader.training_data,
                use_container_width=True,
                height=400
            )


# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>AI Accounting Mapper v1.0.0 | Built with ❤️ for Accounting Excellence</p>
    </div>
    """,
    unsafe_allow_html=True
)
