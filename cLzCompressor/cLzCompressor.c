#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include "fastlz.h"

#define dbg_printf(...) // printf(__VA_ARGS__)

int main(int argc, char** argv)
{
    // Basic arg check
    if(argc < 2)
    {
        fprintf(stderr, "Must give a filename\n");
        return EXIT_FAILURE;
    }

    // Open the file
    FILE* binFile = fopen(argv[1], "r");
    if (NULL != binFile)
    {
        dbg_printf("opened %s.bin\n", argv[1]);

        // See how big the file is
        fseek(binFile, 0, SEEK_END);
        long fsize = ftell(binFile);
        fseek(binFile, 0, SEEK_SET);
        dbg_printf("%s is %ld bytes long\n", argv[1], fsize);

        // Read the entire file
        uint8_t* bytes = malloc(fsize);
        size_t sizeRead = fread(bytes, sizeof(uint8_t), fsize, binFile);
        fclose(binFile);
        dbg_printf("Read %ld bytes\n", sizeRead);

        // Compress the file
        uint8_t* compressedBytes = (uint8_t*)malloc(fsize);
        uint32_t compressedLen = fastlz_compress(bytes, fsize, compressedBytes);
        dbg_printf("Compressed %ld bytes into %d bytes\n", fsize, compressedLen);

        // Print the compressed bytes
        for (uint32_t bIndex = 0; bIndex < compressedLen; bIndex++)
        {
            printf("%02x ", compressedBytes[bIndex]);
        }
        printf("\n");

        // Cleanup
        free(bytes);
        free(compressedBytes);
    }
    return EXIT_SUCCESS;
}
