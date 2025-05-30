# CorpChat Analytics

A comprehensive data analysis and visualization dashboard powered by Synaptide AI. Transform your business data into actionable insights with powerful analytics tools and natural language AI assistance.

## Features

- **Interactive Data Upload**: Support for CSV and Excel files with automatic type detection
- **Advanced Visualizations**: Create bar charts, line graphs, scatter plots, heatmaps, and correlation matrices
- **AI-Powered Analysis**: Natural language queries with Synaptide AI for intelligent data insights
- **Data Cleaning Tools**: Handle missing values, outliers, and data preprocessing
- **Statistical Analysis**: Comprehensive statistical calculations and distribution analysis
- **Responsive Design**: Clean, modern interface with light/dark mode support
- **Professional Styling**: Space Grotesk typography with elegant black/white/gray color scheme

## Tech Stack

- **Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly, Matplotlib, Seaborn
- **AI Integration**: OpenAI API
- **Styling**: Custom CSS, SVG graphics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/corpchat-analytics.git
cd corpchat-analytics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. Run the application:
```bash
streamlit run app.py
```

## Configuration

The app uses Streamlit's configuration system. Key settings are in `.streamlit/config.toml`:

- Server runs on port 5000
- Light theme is default
- Custom styling via CSS files

## Usage

1. **Upload Data**: Use the sidebar to upload CSV or Excel files
2. **Explore Data**: View data preview and basic statistics
3. **Analyze**: Use the Analysis tab for statistical insights
4. **Visualize**: Create charts in the Visualization tab
5. **AI Assistant**: Ask questions about your data using natural language

## Project Structure

```
corpchat-analytics/
├── app.py                 # Main application file
├── components/            # UI components
│   ├── sidebar.py
│   ├── data_preview.py
│   ├── analysis_section.py
│   ├── visualization_section.py
│   └── chat_bot.py
├── utils/                 # Utility functions
│   ├── data_loader.py
│   ├── data_analysis.py
│   └── data_visualization.py
├── assets/               # Static assets
│   ├── backgrounds/
│   └── example_images/
├── .streamlit/           # Streamlit configuration
└── requirements.txt      # Dependencies
```

## Environment Variables

- `OPENAI_API_KEY`: Required for AI-powered analysis features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support, please open an issue on GitHub.