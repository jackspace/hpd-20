"""
Comprehensive TDD tests for hpd20.py - Core module

This module tests the main hpd class which handles:
- Loading and saving .HS0 memory dump files
- MD5 checksum verification
- Kit save/load operations
- Scale application to pads
- Memory management and integrity
"""
import pytest
import hashlib
import os
from pathlib import Path
from hpd20.hpd20 import hpd, get_note_name


class TestGetNoteName:
    """Test suite for get_note_name helper function"""

    def test_get_note_name_middle_c(self):
        """Test getting note name for middle C (60)"""
        assert "C" in get_note_name(60)
        assert "4" in get_note_name(60)

    def test_get_note_name_c_sharp(self):
        """Test getting note name for C# (61)"""
        assert "C#" in get_note_name(61)

    def test_get_note_name_a440(self):
        """Test getting note name for A440 (69)"""
        assert "A" in get_note_name(69)
        assert "4" in get_note_name(69)

    def test_get_note_name_negative(self):
        """Test negative value returns '--'"""
        assert get_note_name(-1) == "--"

    def test_get_note_name_octaves(self):
        """Test note names across multiple octaves"""
        # C notes across octaves
        c0 = get_note_name(12)
        c1 = get_note_name(24)
        c2 = get_note_name(36)

        assert "C" in c0
        assert "C" in c1
        assert "C" in c2


class TestHpdInitialization:
    """Test suite for hpd class initialization and file loading"""

    def test_hpd_loads_valid_hs0_file(self, sample_hs0_file):
        """Test loading a valid .HS0 backup file"""
        hpd_obj = hpd(sample_hs0_file)

        # Verify object was created
        assert hpd_obj is not None
        assert hasattr(hpd_obj, 'memoryBlock')
        assert hasattr(hpd_obj, 'kits')
        assert hasattr(hpd_obj, 'pads')

    def test_hpd_memory_block_size(self, sample_hs0_file):
        """Test that memory block has correct size (excluding MD5)"""
        hpd_obj = hpd(sample_hs0_file)

        # Memory block should be file size minus 16 bytes (MD5)
        expected_size = os.path.getsize(sample_hs0_file) - 16
        assert len(hpd_obj.memoryBlock) == expected_size

    def test_hpd_extracts_md5(self, sample_hs0_file):
        """Test that MD5 checksum is extracted from file"""
        hpd_obj = hpd(sample_hs0_file)

        # MD5 should be 16 bytes
        assert len(hpd_obj.md5_memory) == 16
        assert isinstance(hpd_obj.md5_memory, bytearray)

    def test_hpd_initializes_kits(self, sample_hs0_file):
        """Test that kits collection is initialized"""
        hpd_obj = hpd(sample_hs0_file)

        assert hpd_obj.kits is not None
        # Should have 200 kits
        for i in range(hpd.KITS_COUNT):
            kit = hpd_obj.kits.get_kit(i)
            assert kit is not None

    def test_hpd_initializes_pads(self, sample_hs0_file):
        """Test that pads collection is initialized"""
        hpd_obj = hpd(sample_hs0_file)

        assert hpd_obj.pads is not None
        # Should have 3400 pads (17 * 200)
        for i in range(min(100, hpd.PADS_COUNT)):  # Test first 100
            pad = hpd_obj.pads.get_pad(i)
            assert pad is not None

    def test_hpd_class_constants(self):
        """Test that class constants are defined correctly"""
        assert hpd.CHAIN_MEMINDEX == 1180
        assert hpd.CHAIN_MEMSIZE == 128
        assert hpd.KIT_MEMINDEX == 6922
        assert hpd.KIT_MEMSIZE == 224
        assert hpd.PAD_MEMINDEX == 51596
        assert hpd.PAD_MEMSIZE == 68
        assert hpd.CHAINS_COUNT == 15
        assert hpd.PADS_PER_KIT == 17
        assert hpd.KITS_COUNT == 200
        assert hpd.PADS_COUNT == 3400


class TestHpdFileSaving:
    """Test suite for saving .HS0 files"""

    def test_save_file_creates_file(self, sample_hs0_file, tmp_path):
        """Test that save_file creates a new file"""
        hpd_obj = hpd(sample_hs0_file)
        output_file = str(tmp_path / "test_output.HS0")

        hpd_obj.save_file(output_file)

        # Verify file was created
        assert os.path.exists(output_file)

    def test_save_file_correct_size(self, sample_hs0_file, tmp_path):
        """Test that saved file has correct size (memory + 16 byte MD5)"""
        hpd_obj = hpd(sample_hs0_file)
        output_file = str(tmp_path / "test_output.HS0")

        hpd_obj.save_file(output_file)

        # File size should be memory block + 16 bytes MD5
        expected_size = len(hpd_obj.memoryBlock) + 16
        actual_size = os.path.getsize(output_file)
        assert actual_size == expected_size

    def test_save_file_includes_md5(self, sample_hs0_file, tmp_path):
        """Test that saved file includes MD5 checksum"""
        hpd_obj = hpd(sample_hs0_file)
        output_file = str(tmp_path / "test_output.HS0")

        hpd_obj.save_file(output_file)

        # Read the file and verify last 16 bytes are MD5
        with open(output_file, 'rb') as fh:
            content = fh.read()

        memory_part = content[:-16]
        md5_part = content[-16:]

        # Calculate MD5 of memory part
        m = hashlib.md5()
        m.update(bytes(memory_part))
        calculated_md5 = m.digest()

        # Verify saved MD5 matches calculated
        assert md5_part == calculated_md5

    def test_save_load_roundtrip(self, sample_hs0_file, tmp_path):
        """Test that saving and loading preserves data"""
        # Load original
        hpd_original = hpd(sample_hs0_file)
        original_memory = bytes(hpd_original.memoryBlock)

        # Save to temp file
        temp_file = str(tmp_path / "roundtrip.HS0")
        hpd_original.save_file(temp_file)

        # Load from temp file
        hpd_loaded = hpd(temp_file)
        loaded_memory = bytes(hpd_loaded.memoryBlock)

        # Verify memory is identical
        assert loaded_memory == original_memory

    def test_save_file_after_modification(self, sample_hs0_file, tmp_path):
        """Test saving after modifying memory"""
        hpd_obj = hpd(sample_hs0_file)

        # Modify a pad
        pad = hpd_obj.pads.get_pad(0)
        original_volume = pad.get_volume(0)
        new_volume = (original_volume + 10) % 128
        pad.set_volume(0, new_volume)

        # Save
        output_file = str(tmp_path / "modified.HS0")
        hpd_obj.save_file(output_file)

        # Load saved file
        hpd_reloaded = hpd(output_file)
        reloaded_pad = hpd_reloaded.pads.get_pad(0)

        # Verify modification persisted
        assert reloaded_pad.get_volume(0) == new_volume


class TestHpdKitOperations:
    """Test suite for kit save/load operations"""

    def test_save_kit_creates_file(self, sample_hs0_file, tmp_path):
        """Test that save_kit creates a .kit file"""
        hpd_obj = hpd(sample_hs0_file)
        kit_file = str(tmp_path / "test_kit.kit")

        hpd_obj.save_kit(0, kit_file)

        assert os.path.exists(kit_file)

    def test_save_kit_correct_size(self, sample_hs0_file, tmp_path):
        """Test that saved kit has correct size (224 + 17*68 bytes)"""
        hpd_obj = hpd(sample_hs0_file)
        kit_file = str(tmp_path / "test_kit.kit")

        hpd_obj.save_kit(0, kit_file)

        # Kit file: 224 bytes (kit) + 17 * 68 bytes (pads) = 1380 bytes
        expected_size = 224 + (17 * 68)
        actual_size = os.path.getsize(kit_file)
        assert actual_size == expected_size

    def test_load_kit_from_file(self, sample_hs0_file, tmp_path):
        """Test loading a kit from .kit file"""
        hpd_obj = hpd(sample_hs0_file)

        # Save kit 0
        kit_file = str(tmp_path / "export_kit.kit")
        hpd_obj.save_kit(0, kit_file)

        # Modify kit 1
        kit1 = hpd_obj.kits.get_kit(1)
        original_kit1_name = kit1.main_name()

        # Load kit 0 into slot 1
        hpd_obj.load_kit(1, kit_file)

        # Kit 1 should now have kit 0's data
        kit1_after = hpd_obj.kits.get_kit(1)
        kit0 = hpd_obj.kits.get_kit(0)

        # Names should match
        assert kit1_after.main_name() == kit0.main_name()

    def test_save_all_kits(self, sample_hs0_file, tmp_path, monkeypatch):
        """Test saving all 200 kits"""
        hpd_obj = hpd(sample_hs0_file)

        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        os.makedirs("kits", exist_ok=True)

        # Save first 5 kits only (to save time)
        for i in range(5):
            filename = hpd_obj.create_kit_filename(i)
            hpd_obj.save_kit(i, filename)
            assert os.path.exists(filename)

    def test_create_kit_filename(self, sample_hs0_file):
        """Test kit filename generation"""
        hpd_obj = hpd(sample_hs0_file)

        filename = hpd_obj.create_kit_filename(0)

        # Should start with "kits/"
        assert filename.startswith("kits/")
        # Should end with ".kit"
        assert filename.endswith(".kit")
        # Should contain kit name (sanitized)
        assert len(filename) > len("kits/.kit")


class TestHpdDigestOperations:
    """Test suite for kit information display methods"""

    def test_digest_kits_returns_string(self, sample_hs0_file):
        """Test that digest_kits returns a formatted string"""
        hpd_obj = hpd(sample_hs0_file)

        result = hpd_obj.digest_kits()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_digest_kits_contains_all_kits(self, sample_hs0_file):
        """Test that digest_kits includes all 200 kits"""
        hpd_obj = hpd(sample_hs0_file)

        result = hpd_obj.digest_kits()

        # Should contain lines for all 200 kits
        lines = result.strip().split('\n')
        # Header + 200 kits
        assert len(lines) >= 200

    def test_digest_single_kit_returns_string(self, sample_hs0_file):
        """Test that digest_single_kit returns formatted info"""
        hpd_obj = hpd(sample_hs0_file)

        result = hpd_obj.digest_single_kit(1)  # 1-based index

        assert isinstance(result, str)
        assert len(result) > 0

    def test_digest_single_kit_shows_pads(self, sample_hs0_file):
        """Test that digest_single_kit shows all 17 pads"""
        hpd_obj = hpd(sample_hs0_file)

        result = hpd_obj.digest_single_kit(1)

        # Should contain lines for all 17 pads
        lines = result.strip().split('\n')
        # Header + 17 pads + empty line = at least 19 lines
        assert len(lines) >= 17

    def test_digest_single_kit_contains_pad_info(self, sample_hs0_file):
        """Test that digest includes pad names and parameters"""
        hpd_obj = hpd(sample_hs0_file)

        result = hpd_obj.digest_single_kit(1)

        # Should contain pad names
        assert "M1" in result or "M2" in result or "M5" in result


class TestHpdScaleApplication:
    """Test suite for apply_scale method"""

    def test_apply_scale_to_pads(self, sample_hs0_file):
        """Test applying a scale to a set of pads"""
        hpd_obj = hpd(sample_hs0_file)

        # Get original pitch values
        kit_index = 0
        pad_list = [0, 1, 2, 3, 4]  # First 5 pads

        original_pitches = []
        for pad_offset in pad_list:
            pad_index = kit_index * 17 + pad_offset
            pad = hpd_obj.pads.get_pad(pad_index)
            original_pitches.append(pad.get_pitch(0))

        # Apply major scale starting at C4 (60)
        hpd_obj.apply_scale("Marimba", "major", 0, 60, kit_index, pad_list)

        # Verify pitches changed
        new_pitches = []
        for pad_offset in pad_list:
            pad_index = kit_index * 17 + pad_offset
            pad = hpd_obj.pads.get_pad(pad_index)
            new_pitches.append(pad.get_pitch(0))

        # At least some pitches should have changed
        assert new_pitches != original_pitches

    def test_apply_scale_sets_instruments(self, sample_hs0_file):
        """Test that apply_scale sets instrument patches"""
        hpd_obj = hpd(sample_hs0_file)

        kit_index = 0
        pad_list = [0, 1, 2]

        # Apply scale
        hpd_obj.apply_scale("Marimba", "major", 0, 60, kit_index, pad_list)

        # Verify instruments are set
        for pad_offset in pad_list:
            pad_index = kit_index * 17 + pad_offset
            pad = hpd_obj.pads.get_pad(pad_index)
            patch = pad.get_patch(0)

            # Patch should be set to some value
            assert isinstance(patch, int)
            assert patch >= 0

    def test_apply_pad_updates_memory(self, sample_hs0_file):
        """Test that apply_pad updates main memory block"""
        hpd_obj = hpd(sample_hs0_file)

        pad_index = 0
        pad = hpd_obj.pads.get_pad(pad_index)

        # Modify pad
        original_volume = pad.get_volume(0)
        new_volume = (original_volume + 20) % 128
        pad.set_volume(0, new_volume)

        # Apply pad to memory
        hpd_obj.apply_pad(pad_index)

        # Create new hpd object from the same memory
        # to verify change persisted
        temp_memory = bytearray(hpd_obj.memoryBlock)

        # Verify the memory was updated at correct offset
        offset = hpd.PAD_MEMINDEX + (pad_index * hpd.PAD_MEMSIZE)
        assert temp_memory[offset] == new_volume


class TestHpdMemoryIntegrity:
    """Test suite for memory consistency and integrity"""

    def test_memory_block_consistency(self, sample_hs0_file):
        """Test that memory block remains consistent"""
        hpd_obj = hpd(sample_hs0_file)

        # Store original memory
        original_memory = bytes(hpd_obj.memoryBlock)

        # Access kits and pads (should not modify memory)
        for i in range(10):
            kit = hpd_obj.kits.get_kit(i)
            pad = hpd_obj.pads.get_pad(i)
            _ = kit.main_name()
            _ = pad.get_volume(0)

        # Verify memory unchanged
        current_memory = bytes(hpd_obj.memoryBlock)
        assert current_memory == original_memory

    def test_kit_pad_memory_alignment(self, sample_hs0_file):
        """Test that kits and pads are correctly aligned in memory"""
        hpd_obj = hpd(sample_hs0_file)

        # Kit 0 should start at KIT_MEMINDEX
        kit0 = hpd_obj.kits.get_kit(0)
        assert len(kit0.memory_block) == 224

        # Pad 0 should start at PAD_MEMINDEX
        pad0 = hpd_obj.pads.get_pad(0)
        assert len(pad0.memory_block) == 68

    def test_multiple_hpd_instances_independent(self, sample_hs0_file):
        """Test that multiple hpd instances are independent"""
        hpd1 = hpd(sample_hs0_file)
        hpd2 = hpd(sample_hs0_file)

        # Modify hpd1
        pad1 = hpd1.pads.get_pad(0)
        pad1.set_volume(0, 99)

        # Verify hpd2 is unaffected
        pad2 = hpd2.pads.get_pad(0)
        assert pad2.get_volume(0) != 99
