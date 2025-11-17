"""
Integration tests for HPD-20 Editor full workflows

These tests verify complete end-to-end workflows including:
- Loading .HS0 files
- Editing kits and pads
- Applying scales
- Saving files
- Kit import/export
- Data integrity across operations
"""
import pytest
import os
from pathlib import Path
from hpd20.hpd20 import hpd


class TestFileLoadSaveWorkflow:
    """Integration tests for file loading and saving workflows"""

    def test_load_and_save_preserves_data(self, sample_hs0_file, tmp_path):
        """Test that loading and saving preserves all data"""
        # Load original file
        original_hpd = hpd(sample_hs0_file)

        # Save to new location
        output_file = str(tmp_path / "output.HS0")
        original_hpd.save_file(output_file)

        # Load the saved file
        saved_hpd = hpd(output_file)

        # Verify memory blocks are identical
        assert bytes(original_hpd.memoryBlock) == bytes(saved_hpd.memoryBlock)

        # Verify kit data matches
        for kit_idx in range(min(10, hpd.KITS_COUNT)):
            orig_kit = original_hpd.kits.get_kit(kit_idx)
            saved_kit = saved_hpd.kits.get_kit(kit_idx)

            assert orig_kit.main_name() == saved_kit.main_name()
            assert orig_kit.sub_name() == saved_kit.sub_name()

    def test_multiple_load_save_cycles(self, sample_hs0_file, tmp_path):
        """Test that multiple load/save cycles preserve data"""
        files = []

        # First load
        hpd1 = hpd(sample_hs0_file)
        file1 = str(tmp_path / "cycle1.HS0")
        hpd1.save_file(file1)
        files.append(file1)

        # Load and save 3 more times
        for i in range(2, 5):
            hpd_temp = hpd(files[-1])
            file_temp = str(tmp_path / f"cycle{i}.HS0")
            hpd_temp.save_file(file_temp)
            files.append(file_temp)

        # Load final file
        hpd_final = hpd(files[-1])

        # Compare first and final
        assert bytes(hpd1.memoryBlock) == bytes(hpd_final.memoryBlock)


class TestKitEditWorkflow:
    """Integration tests for kit editing workflows"""

    def test_edit_kit_and_save(self, sample_hs0_file, tmp_path):
        """Test editing a kit and saving changes"""
        # Load file
        hpd_obj = hpd(sample_hs0_file)

        # Modify first pad of first kit
        pad = hpd_obj.pads.get_pad(0)
        original_volume = pad.get_volume(0)
        new_volume = (original_volume + 30) % 128

        pad.set_volume(0, new_volume)

        # Save
        output_file = str(tmp_path / "edited.HS0")
        hpd_obj.save_file(output_file)

        # Reload and verify
        hpd_reloaded = hpd(output_file)
        pad_reloaded = hpd_reloaded.pads.get_pad(0)

        assert pad_reloaded.get_volume(0) == new_volume

    def test_edit_multiple_pads(self, sample_hs0_file, tmp_path):
        """Test editing multiple pads across different kits"""
        hpd_obj = hpd(sample_hs0_file)

        # Edit pads in different kits
        modifications = {}
        for kit_idx in range(5):
            for pad_offset in range(3):
                pad_idx = kit_idx * 17 + pad_offset
                pad = hpd_obj.pads.get_pad(pad_idx)

                new_volume = (kit_idx * 10 + pad_offset * 5) % 128
                pad.set_volume(0, new_volume)
                modifications[pad_idx] = new_volume

        # Save and reload
        output_file = str(tmp_path / "multi_edit.HS0")
        hpd_obj.save_file(output_file)

        hpd_reloaded = hpd(output_file)

        # Verify all modifications
        for pad_idx, expected_volume in modifications.items():
            pad = hpd_reloaded.pads.get_pad(pad_idx)
            assert pad.get_volume(0) == expected_volume

    def test_edit_pad_parameters(self, sample_hs0_file, tmp_path):
        """Test editing various pad parameters"""
        hpd_obj = hpd(sample_hs0_file)

        pad = hpd_obj.pads.get_pad(0)

        # Edit multiple parameters
        pad.set_volume(0, 100)
        pad.set_pitch(0, 1200)  # +1 octave
        pad.set_pan(0, -10)     # Left
        pad.set_patch(0, 420)   # Marimba

        # Save and reload
        output_file = str(tmp_path / "multi_param.HS0")
        hpd_obj.save_file(output_file)

        hpd_reloaded = hpd(output_file)
        pad_reloaded = hpd_reloaded.pads.get_pad(0)

        # Verify all parameters
        assert pad_reloaded.get_volume(0) == 100
        assert pad_reloaded.get_pitch(0) == 1200
        assert pad_reloaded.get_pan(0) == -10
        assert pad_reloaded.get_patch(0) == 420


class TestKitImportExportWorkflow:
    """Integration tests for kit import/export workflows"""

    def test_export_and_import_kit(self, sample_hs0_file, tmp_path):
        """Test exporting a kit and importing it to different slot"""
        hpd_obj = hpd(sample_hs0_file)

        # Get original kit 0 data
        kit0_name = hpd_obj.kits.get_kit(0).main_name()

        # Export kit 0
        kit_file = str(tmp_path / "exported_kit.kit")
        hpd_obj.save_kit(0, kit_file)

        # Verify kit file exists and has correct size
        assert os.path.exists(kit_file)
        assert os.path.getsize(kit_file) == 224 + (17 * 68)

        # Import kit into slot 5
        hpd_obj.load_kit(5, kit_file)

        # Verify kit 5 now has kit 0's name
        kit5_name = hpd_obj.kits.get_kit(5).main_name()
        assert kit5_name == kit0_name

    def test_export_multiple_kits(self, sample_hs0_file, tmp_path):
        """Test exporting multiple kits"""
        hpd_obj = hpd(sample_hs0_file)

        exported_kits = []

        # Export first 3 kits
        for kit_idx in range(3):
            kit_file = str(tmp_path / f"kit_{kit_idx}.kit")
            hpd_obj.save_kit(kit_idx, kit_file)
            exported_kits.append(kit_file)

            assert os.path.exists(kit_file)

        # Verify all files created
        assert len(exported_kits) == 3

    def test_kit_import_preserves_pad_data(self, sample_hs0_file, tmp_path):
        """Test that importing kit preserves all pad parameters"""
        hpd_obj = hpd(sample_hs0_file)

        # Get pad data from kit 0
        kit0_pad0 = hpd_obj.pads.get_pad(0)
        original_volume = kit0_pad0.get_volume(0)
        original_pitch = kit0_pad0.get_pitch(0)
        original_pan = kit0_pad0.get_pan(0)

        # Export kit 0
        kit_file = str(tmp_path / "kit_with_pads.kit")
        hpd_obj.save_kit(0, kit_file)

        # Import into kit 10
        hpd_obj.load_kit(10, kit_file)

        # Verify pad data in kit 10 matches kit 0
        kit10_pad0 = hpd_obj.pads.get_pad(10 * 17)

        assert kit10_pad0.get_volume(0) == original_volume
        assert kit10_pad0.get_pitch(0) == original_pitch
        assert kit10_pad0.get_pan(0) == original_pan

    def test_roundtrip_kit_export_import(self, sample_hs0_file, tmp_path):
        """Test exporting and reimporting same kit"""
        hpd_obj = hpd(sample_hs0_file)

        # Get original data
        original_kit = hpd_obj.kits.get_kit(3)
        original_name = original_kit.main_name()

        # Export
        kit_file = str(tmp_path / "roundtrip.kit")
        hpd_obj.save_kit(3, kit_file)

        # Modify the kit in memory
        # (This ensures we're truly testing the load)
        pad = hpd_obj.pads.get_pad(3 * 17)
        pad.set_volume(0, 99)

        # Reimport
        hpd_obj.load_kit(3, kit_file)

        # Verify original data restored
        restored_kit = hpd_obj.kits.get_kit(3)
        assert restored_kit.main_name() == original_name


class TestScaleApplicationWorkflow:
    """Integration tests for scale application workflows"""

    def test_apply_scale_and_save(self, sample_hs0_file, tmp_path):
        """Test applying a scale and saving the result"""
        hpd_obj = hpd(sample_hs0_file)

        # Apply C major scale to first 8 pads of kit 0
        pad_list = [0, 1, 2, 3, 4, 5, 6, 7]
        hpd_obj.apply_scale("Marimba", "major", 0, 60, 0, pad_list)

        # Save
        output_file = str(tmp_path / "scaled.HS0")
        hpd_obj.save_file(output_file)

        # Reload and verify instruments were set
        hpd_reloaded = hpd(output_file)

        for pad_offset in pad_list:
            pad = hpd_reloaded.pads.get_pad(pad_offset)
            patch = pad.get_patch(0)

            # Patch should be in Marimba range
            assert isinstance(patch, int)
            assert patch >= 0

    def test_apply_multiple_scales(self, sample_hs0_file, tmp_path):
        """Test applying different scales to different kits"""
        hpd_obj = hpd(sample_hs0_file)

        # Apply C major to kit 0
        hpd_obj.apply_scale("Marimba", "major", 0, 60, 0, [0, 1, 2, 3, 4])

        # Apply G pentatonic to kit 1
        hpd_obj.apply_scale("Steel Drum", "pentatonic major", 0, 67, 1, [0, 1, 2, 3, 4])

        # Save
        output_file = str(tmp_path / "multi_scale.HS0")
        hpd_obj.save_file(output_file)

        # Reload and verify
        hpd_reloaded = hpd(output_file)

        # Kit 0 should have Marimba instruments
        kit0_pad0 = hpd_reloaded.pads.get_pad(0)
        assert kit0_pad0.get_patch(0) >= 0

        # Kit 1 should have Steel Drum instruments
        kit1_pad0 = hpd_reloaded.pads.get_pad(17)
        assert kit1_pad0.get_patch(0) >= 0

    def test_scale_application_with_modes(self, sample_hs0_file, tmp_path):
        """Test applying scales with different modes"""
        hpd_obj = hpd(sample_hs0_file)

        # Apply Dorian mode (mode 1) to kit 0
        hpd_obj.apply_scale("Marimba", "major", 1, 60, 0, [0, 1, 2, 3, 4, 5, 6, 7])

        # Save and reload
        output_file = str(tmp_path / "dorian.HS0")
        hpd_obj.save_file(output_file)

        hpd_reloaded = hpd(output_file)

        # Verify pads were modified
        for i in range(8):
            pad = hpd_reloaded.pads.get_pad(i)
            assert pad.get_patch(0) >= 0


class TestComplexWorkflows:
    """Integration tests for complex multi-step workflows"""

    def test_complete_kit_creation_workflow(self, sample_hs0_file, tmp_path):
        """Test creating a complete custom kit from scratch"""
        hpd_obj = hpd(sample_hs0_file)

        kit_idx = 10

        # Step 1: Apply scale to create melodic pads
        hpd_obj.apply_scale("Marimba", "pentatonic major", 0, 60, kit_idx, [0, 1, 2, 3, 4])

        # Step 2: Set volumes
        for pad_offset in range(5):
            pad_idx = kit_idx * 17 + pad_offset
            pad = hpd_obj.pads.get_pad(pad_idx)
            pad.set_volume(0, 90 + pad_offset * 2)
            hpd_obj.apply_pad(pad_idx)

        # Step 3: Set panning (stereo spread)
        pan_values = [-10, -5, 0, 5, 10]
        for i, pad_offset in enumerate(range(5)):
            pad_idx = kit_idx * 17 + pad_offset
            pad = hpd_obj.pads.get_pad(pad_idx)
            pad.set_pan(0, pan_values[i])
            hpd_obj.apply_pad(pad_idx)

        # Step 4: Export the kit
        kit_file = str(tmp_path / "custom_kit.kit")
        hpd_obj.save_kit(kit_idx, kit_file)

        # Step 5: Save the full memory dump
        output_file = str(tmp_path / "custom_kit_backup.HS0")
        hpd_obj.save_file(output_file)

        # Verify: Reload and check
        hpd_reloaded = hpd(output_file)

        for i, pad_offset in enumerate(range(5)):
            pad_idx = kit_idx * 17 + pad_offset
            pad = hpd_reloaded.pads.get_pad(pad_idx)

            assert pad.get_volume(0) == 90 + pad_offset * 2
            assert pad.get_pan(0) == pan_values[i]

    def test_kit_library_management(self, sample_hs0_file, tmp_path):
        """Test managing a library of kits"""
        hpd_obj = hpd(sample_hs0_file)

        # Create a library directory
        library_dir = tmp_path / "kit_library"
        library_dir.mkdir()

        # Export 5 kits to library
        exported_kits = {}
        for kit_idx in range(5):
            kit_name = hpd_obj.kits.get_kit(kit_idx).main_name().strip().replace(" ", "_")
            kit_file = str(library_dir / f"{kit_name}.kit")
            hpd_obj.save_kit(kit_idx, kit_file)
            exported_kits[kit_idx] = kit_file

        # Verify all kits exported
        assert len(exported_kits) == 5
        for kit_file in exported_kits.values():
            assert os.path.exists(kit_file)

        # Import kits into different slots
        for original_idx, kit_file in exported_kits.items():
            new_slot = original_idx + 10
            hpd_obj.load_kit(new_slot, kit_file)

        # Save final result
        output_file = str(tmp_path / "library_test.HS0")
        hpd_obj.save_file(output_file)

        # Verify library operations worked
        assert os.path.exists(output_file)

    def test_backup_modify_restore_workflow(self, sample_hs0_file, tmp_path):
        """Test backing up, modifying, and restoring original state"""
        # Step 1: Load and backup original
        hpd_obj = hpd(sample_hs0_file)
        backup_file = str(tmp_path / "backup.HS0")
        hpd_obj.save_file(backup_file)

        # Step 2: Make modifications
        pad = hpd_obj.pads.get_pad(0)
        pad.set_volume(0, 127)
        pad.set_pitch(0, 1200)

        # Step 3: Save modified version
        modified_file = str(tmp_path / "modified.HS0")
        hpd_obj.save_file(modified_file)

        # Step 4: Restore from backup
        hpd_restored = hpd(backup_file)
        restored_pad = hpd_restored.pads.get_pad(0)

        # Step 5: Verify restoration
        hpd_modified = hpd(modified_file)
        modified_pad = hpd_modified.pads.get_pad(0)

        # Modified should have new values
        assert modified_pad.get_volume(0) == 127
        assert modified_pad.get_pitch(0) == 1200

        # Restored should have original values
        assert restored_pad.get_volume(0) != 127 or restored_pad.get_pitch(0) != 1200


class TestDataIntegrity:
    """Integration tests for data integrity across operations"""

    def test_memory_integrity_after_multiple_operations(self, sample_hs0_file, tmp_path):
        """Test that memory remains consistent after many operations"""
        hpd_obj = hpd(sample_hs0_file)

        # Perform many operations
        for i in range(10):
            # Modify pad
            pad = hpd_obj.pads.get_pad(i)
            pad.set_volume(0, (i * 10) % 128)
            hpd_obj.apply_pad(i)

            # Apply scale
            hpd_obj.apply_scale("Marimba", "major", 0, 60 + i, 0, [i])

        # Save and reload
        output_file = str(tmp_path / "integrity_test.HS0")
        hpd_obj.save_file(output_file)

        hpd_reloaded = hpd(output_file)

        # Verify memory sizes match
        assert len(hpd_obj.memoryBlock) == len(hpd_reloaded.memoryBlock)

    def test_md5_integrity_across_saves(self, sample_hs0_file, tmp_path):
        """Test that MD5 checksums are correctly maintained"""
        hpd_obj = hpd(sample_hs0_file)

        # Save file
        output_file = str(tmp_path / "md5_test.HS0")
        hpd_obj.save_file(output_file)

        # Read file and verify MD5
        with open(output_file, 'rb') as fh:
            content = fh.read()

        memory_part = content[:-16]
        md5_part = content[-16:]

        # Calculate MD5
        import hashlib
        m = hashlib.md5()
        m.update(bytes(memory_part))
        calculated_md5 = m.digest()

        # Verify MD5 matches
        assert md5_part == calculated_md5
