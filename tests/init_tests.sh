#!/bin/bash

# Initialize test environment

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "=============================="
echo "Webbly CMS Test Initialization"
echo "=============================="
echo -e "${NC}"

# Check Python installation
echo -e "\n${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}Python 3 is installed.${NC}"

# Check pip installation
echo -e "\n${YELLOW}Checking pip installation...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Please install pip3 and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}pip3 is installed.${NC}"

# Create virtual environment if it doesn't exist
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"
echo -e "${GREEN}Virtual environment activated.${NC}"

# Install/upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install test dependencies
echo -e "\n${YELLOW}Installing test dependencies...${NC}"
pip install -r "$SCRIPT_DIR/requirements-test.txt"
echo -e "${GREEN}Dependencies installed.${NC}"

# Make initialization script executable
echo -e "\n${YELLOW}Making initialization script executable...${NC}"
chmod +x "$SCRIPT_DIR/init_test_env.py"
echo -e "${GREEN}Script is now executable.${NC}"

# Run initialization script
echo -e "\n${YELLOW}Running test environment initialization...${NC}"
python3 "$SCRIPT_DIR/init_test_env.py"

# Create .env.test if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env.test" ]; then
    echo -e "\n${YELLOW}Creating .env.test file...${NC}"
    cp "$SCRIPT_DIR/.env.test.example" "$SCRIPT_DIR/.env.test" 2>/dev/null || touch "$SCRIPT_DIR/.env.test"
    echo -e "${GREEN}.env.test file created.${NC}"
fi

# Set up pre-commit hooks if git is available
if command -v git &> /dev/null; then
    echo -e "\n${YELLOW}Setting up pre-commit hooks...${NC}"
    
    # Create pre-commit hook
    PRE_COMMIT_HOOK=".git/hooks/pre-commit"
    mkdir -p "$(dirname "$PRE_COMMIT_HOOK")"
    
    cat > "$PRE_COMMIT_HOOK" << 'EOF'
#!/bin/bash

# Run tests before commit
echo "Running tests before commit..."
source tests/venv/bin/activate
pytest tests/unit/  # Run unit tests only for quick feedback

# Check test result
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix the tests before committing."
    exit 1
fi
EOF
    
    chmod +x "$PRE_COMMIT_HOOK"
    echo -e "${GREEN}Pre-commit hooks set up.${NC}"
fi

# Final message
echo -e "\n${GREEN}=============================="
echo "Test environment setup complete!"
echo -e "==============================${NC}"
echo -e "\nNext steps:"
echo "1. Configure test settings in .env.test"
echo "2. Run tests with: pytest"
echo "3. View test reports in tests/reports/"
echo -e "\nHappy testing! 🚀\n"

# Deactivate virtual environment
deactivate
