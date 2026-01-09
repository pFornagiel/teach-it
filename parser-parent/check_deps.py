#!/usr/bin/env python3
"""Check for missing dependencies"""

# Required packages for document loaders
required_packages = {
    # Core Flask
    'flask': 'Web framework',
    'flask-cors': 'CORS support',
    'flask-sqlalchemy': 'Database ORM',
    
    # Database
    'psycopg2-binary': 'PostgreSQL driver',
    'pgvector': 'Vector similarity search',
    'sqlalchemy': 'Database toolkit',
    
    # LangChain
    'langchain': 'LangChain core',
    'langchain-community': 'Community integrations',
    'langchain-core': 'Core abstractions',
    'langchain-openai': 'OpenAI integration',
    'langchain-text-splitters': 'Text splitting',
    
    # OpenAI
    'openai': 'OpenAI API client',
    
    # Document processing
    'unstructured': 'Document loader',
    'unstructured-inference': 'Layout detection & image processing',
    'pdfminer-six': 'PDF text extraction',
    'pypdf': 'PDF processing',
    'pillow': 'Image processing',
    'python-docx': 'Word documents',
    'pandas': 'CSV and data processing',
    'python-magic': 'File type detection',
    
    # Utilities
    'python-dotenv': 'Environment variables',
    'pydantic': 'Data validation',
    'requests': 'HTTP client',
    'werkzeug': 'WSGI utilities',
}

# Read requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.read().lower()

print("=" * 70)
print("DEPENDENCY CHECK FOR UPSIDE HACKATHON")
print("=" * 70)
print()

missing = []
present = []

for package, description in required_packages.items():
    # Normalize package name
    package_normalized = package.lower().replace('_', '-')
    
    # Check if present
    if package_normalized in requirements:
        present.append((package, description))
    else:
        missing.append((package, description))

# Print present packages
print(f"✅ FOUND ({len(present)} packages):")
print("-" * 70)
for pkg, desc in sorted(present):
    print(f"  ✓ {pkg:25s} - {desc}")

print()

# Print missing packages
if missing:
    print(f"❌ MISSING ({len(missing)} packages):")
    print("-" * 70)
    for pkg, desc in sorted(missing):
        print(f"  ✗ {pkg:25s} - {desc}")
    print()
    print("⚠️  Some dependencies may be missing!")
    print("   This could cause errors when processing certain file types.")
    print()
    print("To install missing packages:")
    print("  pip install " + " ".join([pkg for pkg, _ in missing]))
else:
    print("✅ ALL REQUIRED DEPENDENCIES FOUND!")

print()
print("=" * 70)

