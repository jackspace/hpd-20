"""
Comprehensive TDD tests for pad.py module

This module tests Pad and Pads classes which handle:
- Dual-layer instrument support (Layer A & B)
- Pad parameters: volume, pan, pitch, patch, muffling, etc.
- Layer modes: off, mix, velo mix, velo fade, velo sw
- Trigger modes: shot, gate, alt
- All 17 pads per kit × 200 kits = 3,400 pads
"""
import pytest
from hpd20.pad import Pad, Pads


class TestPad:
    """Test suite for Pad class"""

    @pytest.fixture
    def sample_pad_memory(self):
        """Create a sample pad memory block (68 bytes)"""
        memory = bytearray(68)
        # Set some default values for testing
        memory[0] = 80  # Layer A volume
        memory[1] = 60  # Layer B volume
        memory[4] = 0   # Layer A patch low byte
        memory[5] = 1   # Layer A patch high byte
        return memory

    def test_pad_initialization(self, sample_pad_memory):
        """Test Pad initialization with memory block"""
        pad = Pad(sample_pad_memory)
        assert pad.memory_block is sample_pad_memory
        assert len(pad.memory_block) == 68

    # ========== Volume Tests ==========

    def test_get_volume_layer_a(self, sample_pad_memory):
        """Test reading volume for Layer A"""
        pad = Pad(sample_pad_memory)
        volume = pad.get_volume(0)
        assert isinstance(volume, int)
        assert volume == 80

    def test_get_volume_layer_b(self, sample_pad_memory):
        """Test reading volume for Layer B"""
        pad = Pad(sample_pad_memory)
        volume = pad.get_volume(1)
        assert isinstance(volume, int)
        assert volume == 60

    def test_set_volume_layer_a(self):
        """Test setting volume for Layer A"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_volume(0, 100)
        assert pad.get_volume(0) == 100

    def test_set_volume_layer_b(self):
        """Test setting volume for Layer B"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_volume(1, 85)
        assert pad.get_volume(1) == 85

    def test_set_volume_boundary_values(self):
        """Test volume boundary values (0-127)"""
        memory = bytearray(68)
        pad = Pad(memory)

        # Minimum volume
        pad.set_volume(0, 0)
        assert pad.get_volume(0) == 0

        # Maximum volume
        pad.set_volume(0, 127)
        assert pad.get_volume(0) == 127

    # ========== Patch (Instrument) Tests ==========

    def test_get_patch_layer_a(self, sample_pad_memory):
        """Test reading patch number for Layer A"""
        pad = Pad(sample_pad_memory)
        patch = pad.get_patch(0)
        assert isinstance(patch, int)
        # Patch is stored in bytes 4-5 (16-bit)
        assert patch == 256  # 0x0100 in big-endian

    def test_set_patch_layer_a(self):
        """Test setting patch number for Layer A"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_patch(0, 500)
        assert pad.get_patch(0) == 500

    def test_set_patch_layer_b(self):
        """Test setting patch number for Layer B"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_patch(1, 750)
        assert pad.get_patch(1) == 750

    def test_patch_range(self):
        """Test valid patch range (0-1699 for 1700 instruments)"""
        memory = bytearray(68)
        pad = Pad(memory)

        # First instrument
        pad.set_patch(0, 0)
        assert pad.get_patch(0) == 0

        # Last instrument
        pad.set_patch(0, 1699)
        assert pad.get_patch(0) == 1699

    # ========== Pitch Tests ==========

    def test_get_pitch_default(self):
        """Test reading pitch when not set (should be 0)"""
        memory = bytearray(68)
        pad = Pad(memory)
        pitch = pad.get_pitch(0)
        assert pitch == 0

    def test_set_pitch_positive(self):
        """Test setting positive pitch offset (+1200 cents = +1 octave)"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_pitch(0, 1200)
        assert pad.get_pitch(0) == 1200

    def test_set_pitch_negative(self):
        """Test setting negative pitch offset (-1200 cents = -1 octave)"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_pitch(0, -1200)
        assert pad.get_pitch(0) == -1200

    def test_pitch_boundaries(self):
        """Test pitch boundary values (-2400 to +2400 cents)"""
        memory = bytearray(68)
        pad = Pad(memory)

        # Maximum positive pitch
        pad.set_pitch(0, 2400)
        assert pad.get_pitch(0) == 2400

        # Maximum negative pitch
        pad.set_pitch(0, -2400)
        assert pad.get_pitch(0) == -2400

        # Zero pitch
        pad.set_pitch(0, 0)
        assert pad.get_pitch(0) == 0

    def test_pitch_independence_between_layers(self):
        """Test that pitch for Layer A and B are independent"""
        memory = bytearray(68)
        pad = Pad(memory)

        pad.set_pitch(0, 100)
        pad.set_pitch(1, -100)

        assert pad.get_pitch(0) == 100
        assert pad.get_pitch(1) == -100

    # ========== Pan Tests ==========

    def test_set_pan_center(self):
        """Test setting pan to center (0)"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_pan(0, 0)
        assert pad.get_pan(0) == 0

    def test_set_pan_left(self):
        """Test setting pan to full left (-15)"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_pan(0, -15)
        assert pad.get_pan(0) == -15

    def test_set_pan_right(self):
        """Test setting pan to full right (+15)"""
        memory = bytearray(68)
        pad = Pad(memory)
        pad.set_pan(0, 15)
        assert pad.get_pan(0) == 15

    # ========== Layer Tests ==========

    def test_get_layer_default(self):
        """Test getting layer mode (default should be 0=off)"""
        memory = bytearray(68)
        pad = Pad(memory)
        layer_mode = pad.get_layer()
        assert isinstance(layer_mode, int)

    def test_set_layer_modes(self):
        """Test setting different layer modes"""
        memory = bytearray(68)
        pad = Pad(memory)

        layer_modes = [0, 1, 2, 3, 4]  # off, mix, velo mix, velo fade, velo sw
        for mode in layer_modes:
            pad.set_layer(mode)
            assert pad.get_layer() == mode

    # ========== Ambient Send Tests ==========

    def test_get_ambient_send(self):
        """Test reading ambient send level"""
        memory = bytearray(68)
        pad = Pad(memory)
        ambient = pad.get_ambient_send(0)
        assert isinstance(ambient, int)
        assert 0 <= ambient <= 127

    # ========== Muffling Tests ==========

    def test_set_muffling(self):
        """Test setting muffling parameter (0-100)"""
        memory = bytearray(68)
        pad = Pad(memory)

        pad.set_muffling(0, 50)
        assert pad.get_muffling(0) == 50

        pad.set_muffling(0, 0)
        assert pad.get_muffling(0) == 0

        pad.set_muffling(0, 100)
        assert pad.get_muffling(0) == 100

    # ========== Color Tests ==========

    def test_set_color(self):
        """Test setting color parameter (-50 to +50)"""
        memory = bytearray(68)
        pad = Pad(memory)

        pad.set_color(0, 0)
        assert pad.get_color(0) == 0

        pad.set_color(0, -50)
        assert pad.get_color(0) == -50

        pad.set_color(0, 50)
        assert pad.get_color(0) == 50

    # ========== Sweep Tests ==========

    def test_set_sweep(self):
        """Test setting sweep parameter (-100 to +100)"""
        memory = bytearray(68)
        pad = Pad(memory)

        pad.set_sweep(0, 0)
        assert pad.get_sweep(0) == 0

        pad.set_sweep(0, -100)
        assert pad.get_sweep(0) == -100

        pad.set_sweep(0, 100)
        assert pad.get_sweep(0) == 100

    # ========== File I/O Tests ==========

    def test_pad_save(self, sample_pad_memory, tmp_path):
        """Test saving pad to file"""
        pad = Pad(sample_pad_memory)
        test_file = tmp_path / "test_pad.bin"

        with open(test_file, 'wb') as fh:
            pad.save(fh)

        # Verify file size
        assert test_file.stat().st_size == 68

        # Verify content
        with open(test_file, 'rb') as fh:
            saved_data = fh.read()
        assert saved_data == bytes(sample_pad_memory)

    def test_pad_load(self, sample_pad_memory, tmp_path):
        """Test loading pad from file"""
        # Create a test file
        test_file = tmp_path / "test_pad.bin"
        with open(test_file, 'wb') as fh:
            fh.write(sample_pad_memory)

        # Load into a new pad
        empty_memory = bytearray(68)
        pad = Pad(empty_memory)

        with open(test_file, 'rb') as fh:
            pad.load(fh)

        # Verify loaded data matches
        assert pad.get_volume(0) == 80
        assert pad.get_volume(1) == 60

    # ========== Integration Tests ==========

    def test_complete_pad_configuration(self):
        """Test setting all parameters on a pad"""
        memory = bytearray(68)
        pad = Pad(memory)

        # Configure Layer A
        pad.set_volume(0, 100)
        pad.set_patch(0, 420)  # Marimba
        pad.set_pitch(0, 1200)  # +1 octave
        pad.set_pan(0, -5)      # Slightly left
        pad.set_muffling(0, 30)
        pad.set_color(0, 10)
        pad.set_sweep(0, -20)

        # Configure Layer B
        pad.set_volume(1, 80)
        pad.set_patch(1, 421)
        pad.set_pitch(1, 0)
        pad.set_pan(1, 5)       # Slightly right

        # Set layer mode
        pad.set_layer(2)  # velo mix

        # Verify all settings
        assert pad.get_volume(0) == 100
        assert pad.get_patch(0) == 420
        assert pad.get_pitch(0) == 1200
        assert pad.get_pan(0) == -5
        assert pad.get_muffling(0) == 30
        assert pad.get_color(0) == 10
        assert pad.get_sweep(0) == -20

        assert pad.get_volume(1) == 80
        assert pad.get_patch(1) == 421
        assert pad.get_pitch(1) == 0
        assert pad.get_pan(1) == 5

        assert pad.get_layer() == 2


class TestPads:
    """Test suite for Pads collection class"""

    @pytest.fixture
    def sample_pads_memory(self):
        """Create memory block for 3400 pads (68 bytes each = 231,200 bytes)"""
        return bytearray(3400 * 68)

    def test_pads_initialization(self, sample_pads_memory):
        """Test Pads initialization"""
        pads = Pads(sample_pads_memory)
        assert pads.memory_block is sample_pads_memory
        assert len(pads.memory_block) == 3400 * 68

    def test_pads_get_pad_first(self, sample_pads_memory):
        """Test getting the first pad (index 0)"""
        pads = Pads(sample_pads_memory)
        pad = pads.get_pad(0)
        assert isinstance(pad, Pad)
        assert len(pad.memory_block) == 68

    def test_pads_get_pad_last(self, sample_pads_memory):
        """Test getting the last pad (index 3399)"""
        pads = Pads(sample_pads_memory)
        pad = pads.get_pad(3399)
        assert isinstance(pad, Pad)
        assert len(pad.memory_block) == 68

    def test_pads_get_pad_name(self, sample_pads_memory):
        """Test getting pad names"""
        pads = Pads(sample_pads_memory)

        # Test main pads (M1-M5)
        assert "M1" in pads.get_pad_name(0)
        assert "M2" in pads.get_pad_name(1)
        assert "M5" in pads.get_pad_name(4)

        # Test side pads (S1-S8)
        assert "S1" in pads.get_pad_name(5)
        assert "S8" in pads.get_pad_name(12)

        # Test special pads
        assert "D-Beam" in pads.get_pad_name(13)
        assert "Head" in pads.get_pad_name(14)
        assert "Rim" in pads.get_pad_name(15)
        assert "HH" in pads.get_pad_name(16)

    def test_pads_17_per_kit(self, sample_pads_memory):
        """Test that each kit has 17 pads"""
        pads = Pads(sample_pads_memory)

        # Kit 0: pads 0-16
        for i in range(17):
            pad = pads.get_pad(i)
            assert isinstance(pad, Pad)

        # Kit 1: pads 17-33
        for i in range(17, 34):
            pad = pads.get_pad(i)
            assert isinstance(pad, Pad)

    def test_pads_200_kits_total(self, sample_pads_memory):
        """Test that all 200 kits × 17 pads = 3400 pads are accessible"""
        pads = Pads(sample_pads_memory)

        # Test first pad of each kit
        for kit_num in range(200):
            pad_index = kit_num * 17
            pad = pads.get_pad(pad_index)
            assert isinstance(pad, Pad)

    def test_pads_memory_independence(self, sample_pads_memory):
        """Test that each pad has independent memory view"""
        pads = Pads(sample_pads_memory)
        pad1 = pads.get_pad(0)
        pad2 = pads.get_pad(1)

        # They should reference different memory slices
        assert pad1.memory_block is not pad2.memory_block

    def test_pads_modification_reflects_in_memory(self, sample_pads_memory):
        """Test that modifications to a pad affect the main memory"""
        pads = Pads(sample_pads_memory)
        pad = pads.get_pad(10)

        # Modify the pad
        pad.set_volume(0, 99)

        # Verify change is reflected in main memory
        offset = 10 * 68
        assert sample_pads_memory[offset] == 99

    def test_pads_specific_kit_access(self, sample_pads_memory):
        """Test accessing specific pads within a kit"""
        pads = Pads(sample_pads_memory)

        # Kit 5, all 17 pads
        kit_index = 5
        for pad_offset in range(17):
            pad_index = kit_index * 17 + pad_offset
            pad = pads.get_pad(pad_index)
            assert isinstance(pad, Pad)

            # Verify we can set and get values
            pad.set_volume(0, pad_offset + 50)
            assert pad.get_volume(0) == pad_offset + 50
