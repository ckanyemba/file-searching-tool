# ========================================
# 9. tests/test_integration.py
# ========================================

"""
Integration Tests
"""

import pytest
import sys
from pathlib import Path
import tempfile
import shutil

sys.path.append(str(Path(__file__).parent.parent))

from main import QuestionSearchSystem


class TestIntegration:
    
    def setup_method(self):
        # Create temporary database directory
        self.temp_dir = tempfile.mkdtemp()
        self.system = QuestionSearchSystem(database_path=self.temp_dir)
    
    def teardown_method(self):
        # Clean up
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        # This would require actual PDF files
        # For now, just test the system initialization
        assert self.system.database_path.exists()
        assert self.system.extracted_dir.exists()
        assert self.system.vectors_dir.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])