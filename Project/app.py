import streamlit as st
from data_viz_system import DataVizSystem

def main():
    st.title("Advanced Data Visualization System")
    
    # Initialize the visualization system
    if 'viz_system' not in st.session_state:
        st.session_state.viz_system = DataVizSystem()
    
    # File uploader
    st.header("1. Upload Your Dataset")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Load the data
        if st.session_state.viz_system.load_data(uploaded_file):
            st.success("Data loaded successfully!")
            
            # Display data preview
            st.subheader("Data Preview")
            st.dataframe(st.session_state.viz_system.data.head())
            
            # Generate automatic visualizations
            st.header("2. Automatic Key Visualizations")
            visualizations = st.session_state.viz_system.generate_key_visualizations()
            
            for title, fig in visualizations:
                st.subheader(title)
                st.plotly_chart(fig, use_container_width=True)
            
            # Natural language query section
            st.header("3. Natural Language Query Visualization")
            query = st.text_input("Enter your query (e.g., 'Show age distribution' or 'How does gender affect treatment outcome?')")
            
            if query:
                fig, error = st.session_state.viz_system.process_query(query)
                if error:
                    st.error(error)
                else:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Display column information
            st.header("4. Dataset Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Column Types")
                for col, type_ in st.session_state.viz_system.column_types.items():
                    st.write(f"- {col}: {type_}")
            
            with col2:
                st.subheader("Basic Statistics")
                st.write(st.session_state.viz_system.data.describe())

if __name__ == "__main__":
    main()