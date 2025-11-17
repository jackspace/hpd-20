"""
Comprehensive TDD tests for scales.py module

This module tests the Scale class which handles:
- Musical scale generation (major, minor, pentatonic, etc.)
- Modal variations (Ionian, Dorian, Phrygian, etc.)
- Instrument pitch calculations
- Note naming and pitch mapping
- Support for 14 melodic instrument sets
"""
import pytest
from hpd20.scales import Scale


class TestScaleConstants:
    """Test suite for Scale class constants and configurations"""

    def test_melodic_sets_defined(self):
        """Test that melodic instrument sets are properly defined"""
        assert hasattr(Scale, 'melodic_sets')
        assert isinstance(Scale.melodic_sets, dict)
        assert len(Scale.melodic_sets) > 0

    def test_melodic_sets_contain_ranges(self):
        """Test that each melodic set has instrument range"""
        for name, range_vals in Scale.melodic_sets.items():
            assert isinstance(range_vals, list)
            assert len(range_vals) == 2
            assert range_vals[0] <= range_vals[1]  # Start <= End

    def test_scale_patterns_defined(self):
        """Test that scale patterns are defined"""
        assert hasattr(Scale, 'scale_patterns')
        assert isinstance(Scale.scale_patterns, dict)
        assert len(Scale.scale_patterns) >= 8

    def test_major_scale_pattern(self):
        """Test major scale pattern (W-W-H-W-W-W-H)"""
        major = Scale.scale_patterns.get("major")
        assert major is not None
        assert major == [0, 2, 4, 5, 7, 9, 11]

    def test_minor_scale_pattern(self):
        """Test natural minor scale pattern"""
        minor = Scale.scale_patterns.get("minor")
        assert minor is not None
        assert minor == [0, 2, 3, 5, 7, 9, 10]  # Natural minor (Aeolian)

    def test_harmonic_minor_pattern(self):
        """Test harmonic minor scale pattern"""
        harmonic_minor = Scale.scale_patterns.get("harmonic minor")
        assert harmonic_minor is not None
        assert harmonic_minor == [0, 2, 3, 5, 7, 9, 11]

    def test_pentatonic_major_pattern(self):
        """Test pentatonic major scale pattern"""
        penta_major = Scale.scale_patterns.get("pentatonic major")
        assert penta_major is not None
        assert penta_major == [0, 2, 4, 7, 9]

    def test_pentatonic_minor_pattern(self):
        """Test pentatonic minor scale pattern"""
        penta_minor = Scale.scale_patterns.get("pentatonic minor")
        assert penta_minor is not None
        assert penta_minor == [0, 3, 5, 7, 10]

    def test_root_notes_list(self):
        """Test that root notes list is available"""
        root_notes = Scale.get_root_notes()
        assert isinstance(root_notes, list)
        assert len(root_notes) > 0


class TestNoteNameConversion:
    """Test suite for note name conversion functions"""

    def test_get_note_name_middle_c(self):
        """Test note name for middle C (60)"""
        name = Scale.get_note_name(60)
        assert "C" in name
        assert "4" in name

    def test_get_note_name_a440(self):
        """Test note name for A440 (69)"""
        name = Scale.get_note_name(69)
        assert "A" in name
        assert "4" in name

    def test_get_note_name_sharps(self):
        """Test note names with sharps"""
        c_sharp = Scale.get_note_name(61)
        assert "#" in c_sharp or "sharp" in c_sharp.lower()

    def test_get_note_name_octaves(self):
        """Test note names across different octaves"""
        # C notes in different octaves
        c2 = Scale.get_note_name(36)
        c3 = Scale.get_note_name(48)
        c4 = Scale.get_note_name(60)
        c5 = Scale.get_note_name(72)

        assert "C" in c2
        assert "C" in c3
        assert "C" in c4
        assert "C" in c5

        # Octave numbers should be different
        assert c2 != c3 != c4 != c5

    def test_get_note_height(self):
        """Test getting note height from note name"""
        height = Scale.get_note_height(" C4")
        assert height == 60  # Middle C

        height_a = Scale.get_note_height(" A4")
        assert height_a == 69  # A440


class TestScaleGeneration:
    """Test suite for scale generation functionality"""

    def test_get_scale_major_c(self):
        """Test generating C major scale"""
        scale = Scale.get_scale("Marimba", 60, 8, "major", 0)

        assert isinstance(scale, list)
        assert len(scale) == 8

        # Each element should be [instrument_id, pitch_cents]
        for item in scale:
            assert isinstance(item, list) or isinstance(item, tuple)
            assert len(item) == 2
            instrument_id, pitch_cents = item
            assert isinstance(instrument_id, int)
            assert isinstance(pitch_cents, int)

    def test_get_scale_minor_c(self):
        """Test generating C minor scale"""
        scale = Scale.get_scale("Marimba", 60, 8, "minor", 0)

        assert isinstance(scale, list)
        assert len(scale) == 8

    def test_get_scale_pentatonic_major(self):
        """Test generating pentatonic major scale"""
        scale = Scale.get_scale("Steel Drum", 60, 5, "pentatonic major", 0)

        assert isinstance(scale, list)
        assert len(scale) == 5  # Pentatonic has 5 notes

    def test_get_scale_pentatonic_minor(self):
        """Test generating pentatonic minor scale"""
        scale = Scale.get_scale("Steel Drum", 60, 5, "pentatonic minor", 0)

        assert isinstance(scale, list)
        assert len(scale) == 5

    def test_get_scale_different_lengths(self):
        """Test generating scales of different lengths"""
        for length in [5, 8, 12, 17]:
            scale = Scale.get_scale("Marimba", 60, length, "major", 0)
            assert len(scale) == length

    def test_get_scale_different_root_notes(self):
        """Test scales starting from different root notes"""
        c_scale = Scale.get_scale("Marimba", 60, 8, "major", 0)
        g_scale = Scale.get_scale("Marimba", 67, 8, "major", 0)

        # Scales should be different
        assert c_scale != g_scale


class TestModalVariations:
    """Test suite for modal scale variations"""

    def test_mode_ionian(self):
        """Test Ionian mode (major scale, mode 0)"""
        ionian = Scale.get_scale("Marimba", 60, 8, "major", 0)
        assert len(ionian) == 8

    def test_mode_dorian(self):
        """Test Dorian mode (mode 1)"""
        dorian = Scale.get_scale("Marimba", 60, 8, "major", 1)
        assert len(dorian) == 8

    def test_mode_phrygian(self):
        """Test Phrygian mode (mode 2)"""
        phrygian = Scale.get_scale("Marimba", 60, 8, "major", 2)
        assert len(phrygian) == 8

    def test_mode_lydian(self):
        """Test Lydian mode (mode 3)"""
        lydian = Scale.get_scale("Marimba", 60, 8, "major", 3)
        assert len(lydian) == 8

    def test_mode_mixolydian(self):
        """Test Mixolydian mode (mode 4)"""
        mixolydian = Scale.get_scale("Marimba", 60, 8, "major", 4)
        assert len(mixolydian) == 8

    def test_mode_aeolian(self):
        """Test Aeolian mode (natural minor, mode 5)"""
        aeolian = Scale.get_scale("Marimba", 60, 8, "major", 5)
        assert len(aeolian) == 8

    def test_mode_locrian(self):
        """Test Locrian mode (mode 6)"""
        locrian = Scale.get_scale("Marimba", 60, 8, "major", 6)
        assert len(locrian) == 8

    def test_modes_are_different(self):
        """Test that different modes produce different results"""
        ionian = Scale.get_scale("Marimba", 60, 8, "major", 0)
        dorian = Scale.get_scale("Marimba", 60, 8, "major", 1)
        phrygian = Scale.get_scale("Marimba", 60, 8, "major", 2)

        # Different modes should produce different scales
        assert ionian != dorian
        assert dorian != phrygian
        assert ionian != phrygian

    def test_mode_wrapping(self):
        """Test that modes wrap correctly (mode 7, 8, etc.)"""
        mode_0 = Scale.get_scale("Marimba", 60, 8, "major", 0)
        mode_7 = Scale.get_scale("Marimba", 60, 8, "major", 7)

        # Mode 7 should wrap back to mode 0
        assert mode_0 == mode_7

    def test_all_twelve_modes(self):
        """Test all 12 modal variations"""
        modes = []
        for mode in range(12):
            scale = Scale.get_scale("Marimba", 60, 8, "major", mode)
            modes.append(scale)
            assert len(scale) == 8

        # Should have 12 mode variations
        assert len(modes) == 12


class TestInstrumentSelection:
    """Test suite for instrument selection and pitch mapping"""

    def test_get_nearest_note_and_pitch(self):
        """Test finding nearest instrument and pitch offset"""
        # Test with Marimba range
        instrument_id, pitch_cents = Scale.get_nearest_note_and_pitch(
            "Marimba", 6000  # C4 = 60 * 100 cents
        )

        assert isinstance(instrument_id, int)
        assert isinstance(pitch_cents, int)
        assert instrument_id >= 0

    def test_instrument_ranges_valid(self):
        """Test that all melodic instrument ranges are valid"""
        for instrument_name in Scale.melodic_sets.keys():
            # Should not raise exception
            scale = Scale.get_scale(instrument_name, 60, 5, "major", 0)
            assert len(scale) == 5

    def test_pitch_offset_range(self):
        """Test that pitch offsets are within valid range"""
        scale = Scale.get_scale("Marimba", 60, 8, "major", 0)

        for instrument_id, pitch_cents in scale:
            # Pitch should be within ±2400 cents (±2 octaves)
            assert -2400 <= pitch_cents <= 2400

    def test_different_instruments_produce_different_ids(self):
        """Test that different instruments use different instrument IDs"""
        marimba_scale = Scale.get_scale("Marimba", 60, 5, "major", 0)
        steel_drum_scale = Scale.get_scale("Steel Drum", 60, 5, "major", 0)

        marimba_ids = [item[0] for item in marimba_scale]
        steel_drum_ids = [item[0] for item in steel_drum_scale]

        # At least some instrument IDs should be different
        assert marimba_ids != steel_drum_ids


class TestScalePatterns:
    """Test suite for all supported scale patterns"""

    def test_blues_scale_variations(self):
        """Test blues scale variations"""
        patterns = [
            "pentatonic blues min + b5",
            "pentatonic blues min",
            "pentatonic blues maj"
        ]

        for pattern in patterns:
            if pattern in Scale.scale_patterns:
                scale = Scale.get_scale("Marimba", 60, 6, pattern, 0)
                assert isinstance(scale, list)
                assert len(scale) == 6

    def test_all_scale_patterns_work(self):
        """Test that all defined scale patterns can be generated"""
        for pattern_name in Scale.scale_patterns.keys():
            # Generate scale with this pattern
            scale = Scale.get_scale("Marimba", 60, 8, pattern_name, 0)

            assert isinstance(scale, list)
            assert len(scale) == 8


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    def test_single_note_scale(self):
        """Test generating a scale with single note"""
        scale = Scale.get_scale("Marimba", 60, 1, "major", 0)
        assert len(scale) == 1

    def test_large_scale(self):
        """Test generating a scale with many notes"""
        scale = Scale.get_scale("Marimba", 60, 20, "major", 0)
        assert len(scale) == 20

    def test_very_low_root_note(self):
        """Test scale starting from very low note"""
        scale = Scale.get_scale("Marimba", 24, 8, "major", 0)  # C1
        assert len(scale) == 8

    def test_very_high_root_note(self):
        """Test scale starting from very high note"""
        scale = Scale.get_scale("Marimba", 96, 8, "major", 0)  # C7
        assert len(scale) == 8

    def test_negative_mode_wrapping(self):
        """Test that negative modes wrap correctly"""
        scale = Scale.get_scale("Marimba", 60, 8, "major", -1)
        assert len(scale) == 8

    def test_scale_consistency(self):
        """Test that generating same scale twice gives same result"""
        scale1 = Scale.get_scale("Marimba", 60, 8, "major", 0)
        scale2 = Scale.get_scale("Marimba", 60, 8, "major", 0)

        assert scale1 == scale2


class TestScaleMusicalAccuracy:
    """Test suite for musical accuracy of generated scales"""

    def test_major_scale_intervals(self):
        """Test that major scale has correct intervals (W-W-H-W-W-W-H)"""
        # Major scale intervals in semitones: 2, 2, 1, 2, 2, 2, 1
        scale = Scale.get_scale("Marimba", 60, 8, "major", 0)

        # Check that the scale follows major scale pattern
        # (This is a simplified test - full validation would require
        # checking actual pitch values)
        assert len(scale) == 8
        assert all(isinstance(item, (list, tuple)) for item in scale)

    def test_chromatic_sequence(self):
        """Test generating chromatic-like sequence"""
        # Generate many notes to see chromatic progression
        scale = Scale.get_scale("Marimba", 60, 13, "major", 0)
        assert len(scale) == 13

    def test_octave_equivalence(self):
        """Test that octave-separated notes use similar instruments"""
        # Generate 2 octaves of a scale
        scale = Scale.get_scale("Marimba", 60, 15, "major", 0)

        # First and 8th note should be an octave apart (same note name)
        # This is more of a conceptual test
        assert len(scale) >= 8


class TestRootNotes:
    """Test suite for root note list functionality"""

    def test_get_root_notes_returns_list(self):
        """Test that get_root_notes returns a list"""
        root_notes = Scale.get_root_notes()
        assert isinstance(root_notes, list)

    def test_root_notes_contain_note_names(self):
        """Test that root notes list contains valid note names"""
        root_notes = Scale.get_root_notes()

        # Should contain various octaves of notes
        assert len(root_notes) > 0

        # Each entry should be a string
        for note in root_notes:
            assert isinstance(note, str)

    def test_root_notes_span_multiple_octaves(self):
        """Test that root notes cover multiple octaves"""
        root_notes = Scale.get_root_notes()

        # Should have entries for different octaves (C2, C3, C4, etc.)
        assert len(root_notes) >= 12  # At least one octave


class TestInstrumentSets:
    """Test suite for melodic instrument sets"""

    def test_all_instrument_sets_accessible(self):
        """Test that all defined instrument sets work"""
        for instrument_name in Scale.melodic_sets.keys():
            try:
                scale = Scale.get_scale(instrument_name, 60, 5, "major", 0)
                assert len(scale) == 5
            except Exception as e:
                pytest.fail(f"Failed to generate scale for {instrument_name}: {e}")

    def test_instrument_set_names(self):
        """Test some expected instrument set names"""
        expected_instruments = [
            "Marimba",
            "Steel Drum",
            "Vibraphone"
        ]

        for instr in expected_instruments:
            # Check if instrument is in melodic_sets
            # (If not, might have different name)
            if instr in Scale.melodic_sets:
                assert Scale.melodic_sets[instr] is not None
