"""Test documentation and reporting utilities."""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .config import TEST_REPORTS_DIR
from .logging import logger

@dataclass
class TestDoc:
    """Test documentation data."""
    name: str
    description: str
    module: str
    markers: List[str]
    parameters: Optional[Dict[str, Any]] = None
    fixtures: Optional[List[str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None

class TestDocumentation:
    """Test documentation generator."""
    
    def __init__(self):
        self.docs: Dict[str, TestDoc] = {}
    
    def add_doc(self, doc: TestDoc):
        """Add test documentation."""
        self.docs[doc.name] = doc
    
    def generate_markdown(self, output_file: Optional[str] = None) -> str:
        """Generate Markdown documentation."""
        if not output_file:
            output_file = TEST_REPORTS_DIR / f'test_documentation_{datetime.now():%Y%m%d_%H%M%S}.md'
        
        content = self._generate_markdown_content()
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Markdown documentation generated: {output_file}")
        return content
    
    def generate_html(self, output_file: Optional[str] = None) -> str:
        """Generate HTML documentation."""
        if not output_file:
            output_file = TEST_REPORTS_DIR / f'test_documentation_{datetime.now():%Y%m%d_%H%M%S}.html'
        
        content = self._generate_html_content()
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"HTML documentation generated: {output_file}")
        return content
    
    def _generate_markdown_content(self) -> str:
        """Generate Markdown content."""
        lines = [
            "# Test Documentation",
            "",
            "## Overview",
            "",
            f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
            f"Total Tests: {len(self.docs)}",
            "",
            "## Tests",
            ""
        ]
        
        for name, doc in sorted(self.docs.items()):
            lines.extend([
                f"### {name}",
                "",
                doc.description,
                "",
                f"**Module:** {doc.module}",
                "",
                "**Markers:**",
                "".join([f"- {marker}\n" for marker in doc.markers]),
                ""
            ])
            
            if doc.parameters:
                lines.extend([
                    "**Parameters:**",
                    "```python",
                    json.dumps(doc.parameters, indent=2),
                    "```",
                    ""
                ])
            
            if doc.fixtures:
                lines.extend([
                    "**Fixtures:**",
                    "".join([f"- {fixture}\n" for fixture in doc.fixtures]),
                    ""
                ])
            
            if doc.examples:
                lines.extend([
                    "**Examples:**",
                    "```python"
                ])
                for example in doc.examples:
                    lines.extend([
                        f"# {example.get('description', 'Example')}",
                        example.get('code', ''),
                        ""
                    ])
                lines.extend([
                    "```",
                    ""
                ])
            
            if doc.notes:
                lines.extend([
                    "**Notes:**",
                    "",
                    doc.notes,
                    ""
                ])
        
        return "\n".join(lines)
    
    def _generate_html_content(self) -> str:
        """Generate HTML content."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                .test-doc {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; }}
                .description {{ margin: 10px 0; }}
                .metadata {{ margin: 10px 0; }}
                .markers {{ margin: 10px 0; }}
                .parameters {{ margin: 10px 0; background: #f5f5f5; padding: 10px; }}
                .fixtures {{ margin: 10px 0; }}
                .examples {{ margin: 10px 0; }}
                .notes {{ margin: 10px 0; font-style: italic; }}
                pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Test Documentation</h1>
            
            <div class="overview">
                <h2>Overview</h2>
                <p>Generated: {datetime.now():%Y-%m-%d %H:%M:%S}</p>
                <p>Total Tests: {len(self.docs)}</p>
            </div>
            
            <div class="tests">
                <h2>Tests</h2>
                {self._generate_test_docs_html()}
            </div>
        </body>
        </html>
        """
    
    def _generate_test_docs_html(self) -> str:
        """Generate HTML for test documentation."""
        html = []
        
        for name, doc in sorted(self.docs.items()):
            html.append(f"""
            <div class="test-doc">
                <h3>{name}</h3>
                
                <div class="description">
                    {doc.description}
                </div>
                
                <div class="metadata">
                    <strong>Module:</strong> {doc.module}
                </div>
                
                <div class="markers">
                    <strong>Markers:</strong>
                    <ul>
                        {''.join(f'<li>{marker}</li>' for marker in doc.markers)}
                    </ul>
                </div>
            """)
            
            if doc.parameters:
                html.append(f"""
                <div class="parameters">
                    <strong>Parameters:</strong>
                    <pre>{json.dumps(doc.parameters, indent=2)}</pre>
                </div>
                """)
            
            if doc.fixtures:
                html.append(f"""
                <div class="fixtures">
                    <strong>Fixtures:</strong>
                    <ul>
                        {''.join(f'<li>{fixture}</li>' for fixture in doc.fixtures)}
                    </ul>
                </div>
                """)
            
            if doc.examples:
                html.append("""
                <div class="examples">
                    <strong>Examples:</strong>
                """)
                for example in doc.examples:
                    html.append(f"""
                    <div class="example">
                        <p>{example.get('description', 'Example')}</p>
                        <pre>{example.get('code', '')}</pre>
                    </div>
                    """)
                html.append("</div>")
            
            if doc.notes:
                html.append(f"""
                <div class="notes">
                    <strong>Notes:</strong>
                    <p>{doc.notes}</p>
                </div>
                """)
            
            html.append("</div>")
        
        return "\n".join(html)

def document_test(name: str, description: str, module: str, markers: List[str], **kwargs):
    """Decorator to document a test."""
    def decorator(func):
        doc = TestDoc(
            name=name,
            description=description,
            module=module,
            markers=markers,
            **kwargs
        )
        documentation.add_doc(doc)
        return func
    return decorator

# Global documentation instance
documentation = TestDocumentation()
