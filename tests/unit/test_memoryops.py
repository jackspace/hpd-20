"""
Comprehensive TDD tests for memoryops.py module

This module tests all binary memory operations including:
- 8-bit signed/unsigned integer read/write
- 16-bit signed/unsigned integer read/write (big-endian)
- String read/write operations
- Edge cases and boundary conditions
"""
import pytest
from hpd20.memoryops import MemoryOp


class TestMemoryOp:
    """Test suite for MemoryOp class"""

    def test_init_with_valid_memory(self):
        """Test initialization with valid memory block"""
        memory = bytearray(100)
        mem_op = MemoryOp(memory)
        assert mem_op.memory_block is memory

    def test_init_with_empty_memory(self):
        """Test initialization with empty memory block"""
        memory = bytearray()
        mem_op = MemoryOp(memory)
        assert len(mem_op.memory_block) == 0

    # ========== 8-bit Signed Integer Tests ==========

    def test_get_int8_positive(self):
        """Test reading positive 8-bit signed integer"""
        memory = bytearray([0, 50, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_int8(1) == 50

    def test_get_int8_negative(self):
        """Test reading negative 8-bit signed integer"""
        memory = bytearray([0, 200, 0])  # 200 is -56 in signed byte
        mem_op = MemoryOp(memory)
        value = mem_op.get_int8(1)
        # In two's complement, 200 (0xC8) = -56
        assert value == -56

    def test_get_int8_zero(self):
        """Test reading zero value"""
        memory = bytearray([0, 0, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_int8(1) == 0

    def test_get_int8_max_positive(self):
        """Test reading maximum positive value (127)"""
        memory = bytearray([0, 127, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_int8(1) == 127

    def test_get_int8_max_negative(self):
        """Test reading maximum negative value (-128)"""
        memory = bytearray([0, 128, 0])  # 128 = -128 in signed byte
        mem_op = MemoryOp(memory)
        assert mem_op.get_int8(1) == -128

    def test_set_int8_positive(self):
        """Test writing positive 8-bit signed integer"""
        memory = bytearray([0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_int8(1, 75)
        assert memory[1] == 75

    def test_set_int8_negative(self):
        """Test writing negative 8-bit signed integer"""
        memory = bytearray([0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_int8(1, -56)
        # -56 in two's complement is 200
        assert memory[1] == 200

    def test_set_int8_zero(self):
        """Test writing zero value"""
        memory = bytearray([255, 255, 255])
        mem_op = MemoryOp(memory)
        mem_op.set_int8(1, 0)
        assert memory[1] == 0

    def test_set_int8_boundary_values(self):
        """Test writing boundary values (127, -128)"""
        memory = bytearray([0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_int8(0, 127)
        mem_op.set_int8(1, -128)
        assert memory[0] == 127
        assert memory[1] == 128

    # ========== 8-bit Unsigned Integer Tests ==========

    def test_get_unsigned_int8(self):
        """Test reading unsigned 8-bit integer"""
        memory = bytearray([0, 200, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_unsigned_int8(1) == 200

    def test_get_unsigned_int8_max(self):
        """Test reading maximum unsigned value (255)"""
        memory = bytearray([0, 255, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_unsigned_int8(1) == 255

    def test_get_unsigned_int8_min(self):
        """Test reading minimum unsigned value (0)"""
        memory = bytearray([255, 0, 255])
        mem_op = MemoryOp(memory)
        assert mem_op.get_unsigned_int8(1) == 0

    # ========== 16-bit Signed Integer Tests (Big-Endian) ==========

    def test_get_int16_positive(self):
        """Test reading positive 16-bit signed integer (big-endian)"""
        memory = bytearray([0, 0x01, 0x00, 0])  # 256 in big-endian
        mem_op = MemoryOp(memory)
        assert mem_op.get_int16(1) == 256

    def test_get_int16_negative(self):
        """Test reading negative 16-bit signed integer"""
        memory = bytearray([0, 0xFF, 0xFF, 0])  # -1 in big-endian
        mem_op = MemoryOp(memory)
        assert mem_op.get_int16(1) == -1

    def test_get_int16_zero(self):
        """Test reading zero value"""
        memory = bytearray([0, 0x00, 0x00, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_int16(1) == 0

    def test_get_int16_max_positive(self):
        """Test reading maximum positive value (32767)"""
        memory = bytearray([0, 0x7F, 0xFF, 0])  # 32767 in big-endian
        mem_op = MemoryOp(memory)
        assert mem_op.get_int16(1) == 32767

    def test_get_int16_max_negative(self):
        """Test reading maximum negative value (-32768)"""
        memory = bytearray([0, 0x80, 0x00, 0])  # -32768 in big-endian
        mem_op = MemoryOp(memory)
        assert mem_op.get_int16(1) == -32768

    def test_set_int16_positive(self):
        """Test writing positive 16-bit signed integer"""
        memory = bytearray([0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_int16(1, 1000)
        # 1000 = 0x03E8 in big-endian: [0x03, 0xE8]
        assert memory[1] == 0x03
        assert memory[2] == 0xE8

    def test_set_int16_negative(self):
        """Test writing negative 16-bit signed integer"""
        memory = bytearray([0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_int16(1, -1000)
        # -1000 in 16-bit two's complement big-endian
        value = mem_op.get_int16(1)
        assert value == -1000

    def test_set_int16_boundary_values(self):
        """Test writing boundary values"""
        memory = bytearray([0, 0, 0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_int16(0, 32767)
        mem_op.set_int16(2, -32768)
        assert mem_op.get_int16(0) == 32767
        assert mem_op.get_int16(2) == -32768

    # ========== 16-bit Unsigned Integer Tests ==========

    def test_get_unsigned_int16(self):
        """Test reading unsigned 16-bit integer (big-endian)"""
        memory = bytearray([0, 0xFF, 0xFF, 0])  # 65535 in big-endian
        mem_op = MemoryOp(memory)
        assert mem_op.get_unsigned_int16(1) == 65535

    def test_get_unsigned_int16_small(self):
        """Test reading small unsigned value"""
        memory = bytearray([0, 0x00, 0xFF, 0])  # 255 in big-endian
        mem_op = MemoryOp(memory)
        assert mem_op.get_unsigned_int16(1) == 255

    def test_get_unsigned_int16_zero(self):
        """Test reading zero"""
        memory = bytearray([0, 0x00, 0x00, 0])
        mem_op = MemoryOp(memory)
        assert mem_op.get_unsigned_int16(1) == 0

    def test_set_unsigned_int16(self):
        """Test writing unsigned 16-bit integer"""
        memory = bytearray([0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_unsigned_int16(1, 50000)
        assert mem_op.get_unsigned_int16(1) == 50000

    def test_set_unsigned_int16_max(self):
        """Test writing maximum unsigned value (65535)"""
        memory = bytearray([0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        mem_op.set_unsigned_int16(1, 65535)
        assert memory[1] == 0xFF
        assert memory[2] == 0xFF

    # ========== String Operations Tests ==========

    def test_get_string_ascii(self):
        """Test reading ASCII string"""
        memory = bytearray([0] + list(b"Hello") + [0])
        mem_op = MemoryOp(memory)
        result = mem_op.get_string(1, 5)
        assert result == "Hello"

    def test_get_string_with_padding(self):
        """Test reading string with null padding"""
        memory = bytearray([0] + list(b"Test\x00\x00") + [0])
        mem_op = MemoryOp(memory)
        result = mem_op.get_string(1, 6)
        assert result == "Test\x00\x00"

    def test_get_string_empty(self):
        """Test reading empty string region"""
        memory = bytearray([0, 0, 0, 0, 0])
        mem_op = MemoryOp(memory)
        result = mem_op.get_string(1, 3)
        assert result == "\x00\x00\x00"

    def test_set_string_fits_exactly(self):
        """Test writing string that fits exactly"""
        memory = bytearray(10)
        mem_op = MemoryOp(memory)
        mem_op.set_string(1, "Hello", 5)
        result = mem_op.get_string(1, 5)
        assert result == "Hello"

    def test_set_string_with_padding(self):
        """Test writing string shorter than size (should pad with spaces)"""
        memory = bytearray(10)
        mem_op = MemoryOp(memory)
        mem_op.set_string(1, "Hi", 5)
        result = mem_op.get_string(1, 5)
        assert result == "Hi   "

    def test_set_string_truncates(self):
        """Test writing string longer than size (should truncate)"""
        memory = bytearray(10)
        mem_op = MemoryOp(memory)
        mem_op.set_string(1, "HelloWorld", 5)
        result = mem_op.get_string(1, 5)
        assert result == "Hello"

    def test_set_string_empty(self):
        """Test writing empty string"""
        memory = bytearray([255] * 10)
        mem_op = MemoryOp(memory)
        mem_op.set_string(1, "", 5)
        result = mem_op.get_string(1, 5)
        assert result == "     "  # Should be padded with spaces

    # ========== Edge Cases and Error Handling ==========

    def test_operations_at_offset_zero(self):
        """Test operations at the beginning of memory"""
        memory = bytearray([42, 0, 100, 200])
        mem_op = MemoryOp(memory)
        assert mem_op.get_int8(0) == 42
        mem_op.set_int8(0, 99)
        assert memory[0] == 99

    def test_operations_at_end_of_memory(self):
        """Test operations at the end of memory"""
        memory = bytearray([0, 0, 0, 0, 127])
        mem_op = MemoryOp(memory)
        assert mem_op.get_int8(4) == 127

    def test_roundtrip_int8(self):
        """Test writing and reading back 8-bit values"""
        memory = bytearray(10)
        mem_op = MemoryOp(memory)
        test_values = [0, 1, -1, 127, -128, 50, -50]
        for i, value in enumerate(test_values):
            mem_op.set_int8(i, value)
            assert mem_op.get_int8(i) == value

    def test_roundtrip_int16(self):
        """Test writing and reading back 16-bit values"""
        memory = bytearray(20)
        mem_op = MemoryOp(memory)
        test_values = [0, 1, -1, 1000, -1000, 32767, -32768]
        for i, value in enumerate(test_values):
            mem_op.set_int16(i * 2, value)
            assert mem_op.get_int16(i * 2) == value

    def test_string_special_characters(self):
        """Test string operations with special characters"""
        memory = bytearray(20)
        mem_op = MemoryOp(memory)
        test_string = "Test-Kit_123"
        mem_op.set_string(1, test_string, 15)
        result = mem_op.get_string(1, 15)
        assert result.strip() == test_string
