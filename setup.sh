#!/bin/bash
# Setup script for Podcast Organizer

set -e

echo "🎙️  Podcast Organizer - Setup"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure your API key:"
echo "   cp .podcast-organizer.yaml.example .podcast-organizer.yaml"
echo "   # Then edit .podcast-organizer.yaml and add your Anthropic API key"
echo ""
echo "3. Run a test:"
echo "   ./podcast-organizer test-mini.opml --verbose"
echo ""
