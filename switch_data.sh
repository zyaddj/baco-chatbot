#!/bin/bash
# switch_data.sh - Helper script to switch between data sources

echo "🔄 BACO Chatbot Data Source Switcher"
echo "=================================="

# Function to run ingestion
run_ingestion() {
    local data_folder=$1
    local output_folder=$2
    echo "📊 Processing PDFs from $data_folder..."
    python ingest_flexible.py --data_folder "$data_folder" --output_folder "$output_folder"
}

# Function to start app
start_app() {
    local vector_path=$1
    echo "🚀 Starting app with $vector_path..."
    streamlit run app_flexible.py -- --vector_path "$vector_path"
}

case "$1" in
    "original")
        echo "📁 Switching to ORIGINAL data source..."
        if [ -d "data" ] && [ "$(ls -A data/*.pdf 2>/dev/null)" ]; then
            run_ingestion "data" "faiss_index"
            echo "✅ Ready! Starting app..."
            start_app "faiss_index"
        else
            echo "❌ No PDF files found in data/ folder"
        fi
        ;;
    "test")
        echo "🧪 Switching to TEST data source..."
        if [ -d "test_data" ] && [ "$(ls -A test_data/*.pdf 2>/dev/null)" ]; then
            run_ingestion "test_data" "test_vectors"
            echo "✅ Ready! Starting app..."
            start_app "test_vectors"
        else
            echo "❌ No PDF files found in test_data/ folder"
            echo "💡 Add your test PDF files to test_data/ first"
        fi
        ;;
    "ingest-original")
        echo "📊 Processing original data only..."
        run_ingestion "data" "faiss_index"
        ;;
    "ingest-test")
        echo "📊 Processing test data only..."
        run_ingestion "test_data" "test_vectors"
        ;;
    *)
        echo "Usage: $0 {original|test|ingest-original|ingest-test}"
        echo ""
        echo "Commands:"
        echo "  original        - Process original data and start app"
        echo "  test           - Process test data and start app"
        echo "  ingest-original - Only process original data"
        echo "  ingest-test    - Only process test data"
        echo ""
        echo "Current status:"
        echo "📁 Original data: $(ls data/*.pdf 2>/dev/null | wc -l | tr -d ' ') PDF files"
        echo "🧪 Test data: $(ls test_data/*.pdf 2>/dev/null | wc -l | tr -d ' ') PDF files"
        echo "📊 Original vectors: $([ -d "faiss_index" ] && echo "✅ Ready" || echo "❌ Not created")"
        echo "📊 Test vectors: $([ -d "test_vectors" ] && echo "✅ Ready" || echo "❌ Not created")"
        ;;
esac