import os
import sys
import shutil

BLOCK_SIZE = 135168  # 0x21000
EXPECTED_SIZE = 138412032  # 0x8400000

def error(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def write_binary_section(target_file, source_file, seek_blocks):
    offset = BLOCK_SIZE * seek_blocks
    with open(source_file, 'rb') as sf:
        data = sf.read()
    with open(target_file, 'r+b') as tf:
        tf.seek(offset)
        tf.write(data)

def main(infile, outfile):
    if not os.path.exists(infile):
        error("Source image missing")
    if not outfile:
        error("Target image not provided")
    if os.path.abspath(infile) == os.path.abspath(outfile):
        error("Source equals target, will not overwrite the source file")
    if os.path.exists(outfile):
        error("Target image already exists. Refusing to overwrite!")

    if os.path.getsize(infile) != EXPECTED_SIZE:
        error("Source image has invalid size. Was it dumped without OOB data?")

    shutil.copyfile(infile, outfile)

    write_binary_section(outfile, "ubootmr332012.bin", seek_blocks=56)
    write_binary_section(outfile, "ubimr33.bin", seek_blocks=96)
    # Uncomment if restoring ART:
    # write_binary_section(outfile, "art_repaired.bin", seek_blocks=88)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <infile> <outfile>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
