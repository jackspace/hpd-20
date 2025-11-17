"""
TDD tests for kit.py module

This module tests Kit and Kits classes which handle:
- Kit name and subtitle management
- Kit volume, balance, and sensitivity settings
- Multiple kit management (200 kits)
"""
import pytest
from hpd20.kit import Kit, Kits


class TestKit:
    """Test suite for Kit class"""

    @pytest.fixture
    def sample_kit_memory(self):
        """Create a sample kit memory block (224 bytes)"""
        memory = bytearray(224)
        # Set kit name at offset 2 (12 characters)
        kit_name = b"TestKit123  "
        for i, byte in enumerate(kit_name):
            memory[2 + i] = byte
        # Set sub name at offset 14 (16 characters)
        sub_name = b"SubtitleTest    "
        for i, byte in enumerate(sub_name):
            memory[14 + i] = byte
        return memory

    def test_kit_initialization(self, sample_kit_memory):
        """Test Kit initialization with memory block"""
        kit = Kit(sample_kit_memory)
        assert kit.memory_block is sample_kit_memory
        assert len(kit.memory_block) == 224

    def test_kit_main_name(self, sample_kit_memory):
        """Test reading kit main name"""
        kit = Kit(sample_kit_memory)
        name = kit.main_name()
        assert isinstance(name, str)
        assert "TestKit123" in name
        assert len(name) == 12

    def test_kit_sub_name(self, sample_kit_memory):
        """Test reading kit subtitle"""
        kit = Kit(sample_kit_memory)
        sub = kit.sub_name()
        assert isinstance(sub, str)
        assert "SubtitleTest" in sub
        assert len(sub) == 16

    def test_kit_empty_name(self):
        """Test kit with empty name"""
        memory = bytearray(224)
        kit = Kit(memory)
        name = kit.main_name()
        # Should be 12 null or space characters
        assert len(name) == 12
        assert name.strip() == "" or name == "\x00" * 12

    def test_kit_volume(self, sample_kit_memory):
        """Test reading kit volume (0-127)"""
        kit = Kit(sample_kit_memory)
        volume = kit.get_volume()
        assert isinstance(volume, int)
        assert 0 <= volume <= 127

    def test_kit_hh_volume(self, sample_kit_memory):
        """Test reading hi-hat volume"""
        kit = Kit(sample_kit_memory)
        hh_volume = kit.get_hh_volume()
        assert isinstance(hh_volume, int)
        assert 0 <= hh_volume <= 127

    def test_kit_balance(self, sample_kit_memory):
        """Test reading kit balance (-64 to +63)"""
        kit = Kit(sample_kit_memory)
        balance = kit.get_balance()
        assert isinstance(balance, int)
        assert -64 <= balance <= 63

    def test_kit_name_with_special_characters(self):
        """Test kit name with special characters"""
        memory = bytearray(224)
        # Kit name with symbols
        kit_name = b"Rock-Kit #1 "
        for i, byte in enumerate(kit_name):
            memory[2 + i] = byte
        kit = Kit(memory)
        name = kit.main_name()
        assert "Rock-Kit #1" in name

    def test_kit_save(self, sample_kit_memory, tmp_path):
        """Test saving kit to file"""
        kit = Kit(sample_kit_memory)
        test_file = tmp_path / "test_kit.bin"
        with open(test_file, 'wb') as fh:
            kit.save(fh)

        # Verify file size
        assert test_file.stat().st_size == 224

        # Verify content
        with open(test_file, 'rb') as fh:
            saved_data = fh.read()
        assert saved_data == bytes(sample_kit_memory)

    def test_kit_load(self, sample_kit_memory, tmp_path):
        """Test loading kit from file"""
        # Create a test file with known data
        test_file = tmp_path / "test_kit.bin"
        with open(test_file, 'wb') as fh:
            fh.write(sample_kit_memory)

        # Load into a new kit
        empty_memory = bytearray(224)
        kit = Kit(empty_memory)
        with open(test_file, 'rb') as fh:
            kit.load(fh)

        # Verify loaded data matches
        assert kit.main_name() == "TestKit123  "
        assert kit.sub_name() == "SubtitleTest    "


class TestKits:
    """Test suite for Kits collection class"""

    @pytest.fixture
    def sample_kits_memory(self):
        """Create memory block for 200 kits (224 bytes each = 44800 bytes)"""
        memory = bytearray(200 * 224)
        # Populate first few kits with test data
        for kit_num in range(5):
            offset = kit_num * 224
            kit_name = f"Kit{kit_num:03d}     ".encode('ascii')
            for i, byte in enumerate(kit_name):
                memory[offset + 2 + i] = byte
        return memory

    def test_kits_initialization(self, sample_kits_memory):
        """Test Kits initialization with memory block"""
        kits = Kits(sample_kits_memory)
        assert kits.memory_block is sample_kits_memory
        assert len(kits.memory_block) == 200 * 224

    def test_kits_get_kit_first(self, sample_kits_memory):
        """Test getting the first kit (index 0)"""
        kits = Kits(sample_kits_memory)
        kit = kits.get_kit(0)
        assert isinstance(kit, Kit)
        assert "Kit000" in kit.main_name()

    def test_kits_get_kit_last(self, sample_kits_memory):
        """Test getting the last kit (index 199)"""
        kits = Kits(sample_kits_memory)
        kit = kits.get_kit(199)
        assert isinstance(kit, Kit)
        # Last kit should have empty name in our test data
        assert len(kit.main_name()) == 12

    def test_kits_get_kit_middle(self, sample_kits_memory):
        """Test getting a middle kit"""
        kits = Kits(sample_kits_memory)
        kit = kits.get_kit(2)
        assert isinstance(kit, Kit)
        assert "Kit002" in kit.main_name()

    def test_kits_get_list_of_kits(self, sample_kits_memory):
        """Test getting formatted list of all kits"""
        kits = Kits(sample_kits_memory)
        kit_list = kits.get_list_of_kits()

        # Should return a list of strings
        assert isinstance(kit_list, list)
        assert len(kit_list) == 200

        # Check first few kits
        for i in range(5):
            assert f"Kit{i:03d}" in kit_list[i]

    def test_kits_memory_independence(self, sample_kits_memory):
        """Test that each kit has independent memory view"""
        kits = Kits(sample_kits_memory)
        kit1 = kits.get_kit(0)
        kit2 = kits.get_kit(1)

        # They should reference different memory slices
        assert kit1.memory_block is not kit2.memory_block

        # But both should be views of the main memory
        kit1_offset = 0 * 224
        kit2_offset = 1 * 224
        assert bytes(kit1.memory_block) == bytes(sample_kits_memory[kit1_offset:kit1_offset + 224])
        assert bytes(kit2.memory_block) == bytes(sample_kits_memory[kit2_offset:kit2_offset + 224])

    def test_kits_boundary_indices(self, sample_kits_memory):
        """Test boundary kit indices"""
        kits = Kits(sample_kits_memory)

        # First kit (0)
        kit0 = kits.get_kit(0)
        assert isinstance(kit0, Kit)

        # Last kit (199)
        kit199 = kits.get_kit(199)
        assert isinstance(kit199, Kit)

    def test_kits_modification_reflects_in_memory(self, sample_kits_memory):
        """Test that modifications to a kit affect the main memory"""
        kits = Kits(sample_kits_memory)
        kit = kits.get_kit(10)

        # Modify the kit's memory
        kit.memory_block[0] = 99

        # Verify change is reflected in main memory
        assert sample_kits_memory[10 * 224] == 99

    def test_kits_all_200_kits_accessible(self, sample_kits_memory):
        """Test that all 200 kits are accessible"""
        kits = Kits(sample_kits_memory)

        # Access all 200 kits
        for i in range(200):
            kit = kits.get_kit(i)
            assert isinstance(kit, Kit)
            assert len(kit.memory_block) == 224
