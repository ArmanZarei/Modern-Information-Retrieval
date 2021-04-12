class VariableByteCompressor:
    def __bits_to_number(self, arr):
        ans = 0
        for bit in arr:
            ans = ans * 2 + bit

        return ans

    def __number_to_btis_arr(self, n):
        return list(map(int, list(bin(n)[2:])))

    def __number_to_byte(self, number):
        bits = self.__number_to_btis_arr(number)
        while len(bits) % 8 != 0:
            bits.insert(0, 0)

        return bits

    def __transform_number(self, number):
        number_bits = self.__number_to_btis_arr(number)

        while len(number_bits) % 7 != 0:
            number_bits.insert(0, 0)

        result = []

        bytes_count = len(number_bits) // 7
        for i in range(bytes_count):
            tmp = [0] + number_bits[7 * i:7 * i + 7]
            tmp[0] = 1 if i == bytes_count - 1 else 0
            result.append(tmp)

        return result

    def compress_number(self, number):
        transformed_bits_arr = self.__transform_number(number)

        tmp = []
        for b in transformed_bits_arr:
            tmp += b

        return '{0:x}'.format(int("".join(map(str, tmp)), 2))

    def compress_number_list(self, arr):
        transformed_numbers = [self.__transform_number(number) for number in arr]

        tmp = []
        for i in transformed_numbers:
            for j in i:
                tmp += j

        return '{0:x}'.format(int("".join(map(str, tmp)), 2))

    def decompress_string(self, s):
        result = []
        bits = [int(b) for b in '{0:b}'.format(int(s, 16))]

        while len(bits) % 8 != 0:
            bits.insert(0, 0)

        tmp = []
        for i in range(len(bits)//8):
            for bit in bits[8*i+1:8*i + 8]:
                tmp.append(bit)
            if bits[8*i] == 1:
                result.append(self.__bits_to_number(tmp))
                tmp = []

        return result


# ------------------------- Testing ------------------------- #
# variable_byte_compressor = VariableByteCompressor()
#
# test_pos = [23, 232, 20232, 9248, 999999, 100, 200]
# s = variable_byte_compressor.compress_number_list(test_pos)
# print(s)
#
# decomposed = variable_byte_compressor.decompress_string(s)
# print(decomposed)
#
# print('Is Compression/Decompression successful :', all([decomposed[i] == test_pos[i] for i in range(len(test_pos))]))
