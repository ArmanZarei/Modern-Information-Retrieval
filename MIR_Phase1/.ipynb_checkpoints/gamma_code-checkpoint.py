class GammaCodeCompressor:
    def __init__(self):
        self.__shift_amount = 1

    def __number_to_btis_arr(self, n):
        return list(map(int, list(bin(n)[2:])))

    def __transform_number(self, number):
        bits = self.__number_to_btis_arr(number)
        bits.pop(0)
        bits.insert(0, 0)
        for i in range(len(bits) - 1):
            bits.insert(0, 1)

        return bits

    def compress_number_list(self, arr):
        transformed_numbers = [self.__transform_number(number+self.__shift_amount) for number in arr]
        tmp = []
        for i in transformed_numbers:
            tmp += i

        return '{0:x}'.format(int("".join(map(str, tmp)), 2))

    def decompress_string(self, s):
        result = []
        bits = [int(b) for b in '{0:b}'.format(int(s, 16))]
        ptr = 0
        while ptr < len(bits):
            length = 0
            while bits[ptr] == 1:
                length += 1
                ptr += 1
            ptr += 1
            offset = 1
            for i in range(length):
                offset = offset*2 + bits[ptr]
                ptr += 1
            result.append(offset-self.__shift_amount)

        return result


# ------------------------- Testing ------------------------- #
# gamma_code_compressor = GammaCodeCompressor()
#
# test_pos = [1, 2, 23, 232, 20232, 9248, 999999, 100, 200]
# s = gamma_code_compressor.compress_number_list(test_pos)
# print(s)
#
# decomposed = gamma_code_compressor.decompress_string(s)
# print(decomposed)
#
# print('Is Compression/Decompression successful :', all([decomposed[i] == test_pos[i] for i in range(len(test_pos))]))

