"""
Pytest configuration and shared fixtures for HPD-20 Editor tests
"""
import os
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_hs0_file(project_root):
    """Return path to a sample .HS0 backup file"""
    sample_file = project_root / "BKUP-021.HS0"
    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")
    return str(sample_file)


@pytest.fixture
def sample_kit_directory(project_root):
    """Return path to the kits directory"""
    kits_dir = project_root / "kits"
    if not kits_dir.exists():
        pytest.skip(f"Kits directory not found: {kits_dir}")
    return str(kits_dir)


@pytest.fixture
def temp_hs0_file(tmp_path):
    """Create a temporary .HS0 file path for testing"""
    return str(tmp_path / "test_backup.HS0")


@pytest.fixture
def temp_kit_file(tmp_path):
    """Create a temporary .kit file path for testing"""
    return str(tmp_path / "test_kit.kit")


@pytest.fixture
def sample_memory_block():
    """Create a minimal valid memory block for testing"""
    # Create a 282KB memory block (approximate size of .HS0 file)
    memory_size = 282812  # Actual size based on file analysis
    return bytearray(memory_size)


@pytest.fixture
def sample_kit_memory():
    """Create a sample kit memory block (224 bytes)"""
    kit_memory = bytearray(224)
    # Set kit name at offset 2 (12 characters)
    kit_name = b"Test Kit    "
    for i, byte in enumerate(kit_name):
        kit_memory[2 + i] = byte
    # Set sub name at offset 14 (16 characters)
    sub_name = b"Test Subtitle   "
    for i, byte in enumerate(sub_name):
        kit_memory[14 + i] = byte
    return kit_memory


@pytest.fixture
def sample_pad_memory():
    """Create a sample pad memory block (68 bytes)"""
    return bytearray(68)
